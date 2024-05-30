package main

import (
	"bufio"
	"github.com/streadway/amqp"
	"log"
	"os"
	utils "rabbit"
	"sync"
)

// Constants for RabbitMQ connection details
const (
	loggingQueueName = "logging"
)

func main() {
	conn, ch := setupRabbitMQ()
	defer conn.Close()
	defer ch.Close()

	setupExchanges(ch)
	loggingQueue := setupLoggingQueue(ch)

	var wg sync.WaitGroup
	wg.Add(2) // Add 2 because we have 2 goroutines

	go consumeLoggingQueue(ch, loggingQueue.Name, &wg)
	go readAndPublishAdminMessages(ch, &wg)

	select {} // Block forever
}

// setupRabbitMQ initializes the connection and channel for RabbitMQ
func setupRabbitMQ() (*amqp.Connection, *amqp.Channel) {
	conn, err := amqp.Dial(utils.RabbitMQURL)
	utils.FailOnError(err, "Failed to connect to RabbitMQ")

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open the channel")

	return conn, ch
}

// setupExchanges declares the necessary exchanges for the application
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

// setupLoggingQueue declares and binds the logging queue to the operations exchange
func setupLoggingQueue(ch *amqp.Channel) amqp.Queue {
	loggingQueue, err := ch.QueueDeclare(
		loggingQueueName,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the logging queue")

	err = ch.QueueBind(
		loggingQueue.Name,
		loggingQueue.Name,
		utils.OperationsExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the logging queue")

	return loggingQueue
}

// consumeLoggingQueue consumes messages from the logging queue and logs them
func consumeLoggingQueue(ch *amqp.Channel, queueName string, wg *sync.WaitGroup) {
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

	for d := range msgs {
		log.Print(string(d.Body))
	}
}

// readAndPublishAdminMessages reads input from stdin and publishes it to the administration exchange
func readAndPublishAdminMessages(ch *amqp.Channel, wg *sync.WaitGroup) {
	defer wg.Done()
	reader := bufio.NewReader(os.Stdin)

	for {
		input, err := reader.ReadString('\n')
		utils.FailOnError(err, "Failed to read from stdin")
		err = ch.Publish(
			utils.AdministrationExchange,
			"",
			false,
			false,
			amqp.Publishing{
				ContentType: "text/plain",
				Body:        []byte(input),
			},
		)
		utils.FailOnError(err, "Failed to publish a message")
	}
}
