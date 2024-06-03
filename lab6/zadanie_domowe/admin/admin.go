package main

import (
	"bufio"
	"context"
	"github.com/google/uuid"
	"github.com/streadway/amqp"
	"log"
	"os"
	"os/signal"
	utils "rabbit"
	"sync"
	"syscall"
)

const (
	loggingQueueName = "logging"
)

func main() {
	adminId := uuid.New().String()
	conn, ch := setupRabbitMQ()
	defer conn.Close()
	defer ch.Close()

	setupExchanges(ch)
	loggingQueue := setupLoggingQueue(ch, adminId)

	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup
	wg.Add(2)

	go consumeLoggingQueue(ctx, ch, loggingQueue.Name, &wg)
	go readAndPublishAdminMessages(ctx, ch, &wg)

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-c
		log.Println("Received interrupt signal, shutting down...")
		cancel()
	}()

	wg.Wait()
	log.Println("All goroutines finished, exiting.")
}

func setupRabbitMQ() (*amqp.Connection, *amqp.Channel) {
	conn, err := amqp.Dial(utils.RabbitMQURL)
	utils.FailOnError(err, "Failed to connect to RabbitMQ")

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open the channel")

	return conn, ch
}

func setupExchanges(ch *amqp.Channel) {
	err := ch.ExchangeDeclare(
		utils.AdministrationExchange,
		utils.AdministrationExchangeType,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the administration exchange")

	err = ch.ExchangeDeclare(
		utils.OperationsExchange,
		utils.OperationsExchangeType,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the operations exchange")
}

func setupLoggingQueue(ch *amqp.Channel, adminId string) amqp.Queue {
	loggingQueue, err := ch.QueueDeclare(
		loggingQueueName+"."+adminId,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the logging queue")

	err = ch.QueueBind(
		loggingQueue.Name,
		"logging.#",
		utils.OperationsExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the logging queue")

	return loggingQueue
}

func consumeLoggingQueue(ctx context.Context, ch *amqp.Channel, queueName string, wg *sync.WaitGroup) {
	defer wg.Done()
	msgs, err := ch.Consume(
		queueName,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to register a consumer")

	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping consumeLoggingQueue...")
			return
		case d, ok := <-msgs:
			if !ok {
				return
			}
			log.Print(string(d.Body))
		}
	}
}

func readAndPublishAdminMessages(ctx context.Context, ch *amqp.Channel, wg *sync.WaitGroup) {
	defer wg.Done()
	reader := bufio.NewReader(os.Stdin)

	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping readAndPublishAdminMessages...")
			return
		default:
			input, err := reader.ReadString('\n')
			if err != nil {
				log.Println("Error reading from stdin:", err)
				continue
			}
			utils.SendMessage(ch, utils.AdministrationExchange, "", input, "", false)

		}
	}
}
