package main

import (
	"bufio"
	"context"
	"fmt"
	"github.com/google/uuid"
	"github.com/streadway/amqp"
	"log"
	"math/rand"
	"os"
	"os/signal"
	utils "rabbit"
	"strings"
	"sync"
	"syscall"
	"time"
)

var operations = []string{"knee", "elbow", "hip"}
var messages = []string{"Kowalski", "Nowak", "Burak", "Kowal", "Kowalczyk", "Kowalewski", "Kowalewska", "Kowalik", "Kowalczuk", "Kowalak", "Kowalak"}

type OperationType string

const (
	Knee  OperationType = "knee"
	Elbow OperationType = "elbow"
	Hip   OperationType = "hip"
)

func main() {
	doctorId := uuid.New().String()

	conn, err := amqp.Dial(utils.RabbitMQURL)
	utils.FailOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open a channel")
	defer ch.Close()

	setupExchanges(ch)
	doctorQueueName := setupDoctorQueue(ch, doctorId)
	adminQueueName := setupAdminQueue(ch, doctorId)

	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup
	wg.Add(3)

	go consumeDoctorQueue(ctx, &wg, ch, doctorQueueName)
	//go publishMessages(ctx, &wg, ch, doctorId)
	go consumeAdminQueue(ctx, &wg, ch, adminQueueName)
	go manualMessageInput(ctx, &wg, ch, doctorId)

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

func setupExchanges(ch *amqp.Channel) {
	err := ch.ExchangeDeclare(
		utils.OperationsExchange,
		utils.OperationsExchangeType,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the operations exchange")

	err = ch.ExchangeDeclare(
		utils.AdministrationExchange,
		utils.AdministrationExchangeType,
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the administration exchange")
}

func setupDoctorQueue(ch *amqp.Channel, doctorId string) string {
	doctorQueueName := "doctor_queue_" + doctorId
	q, err := ch.QueueDeclare(
		doctorQueueName,
		false,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the doctor queue")

	err = ch.QueueBind(
		q.Name,
		doctorId,
		utils.OperationsExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the doctor queue")

	return doctorQueueName
}

func setupAdminQueue(ch *amqp.Channel, id string) string {
	q, err := ch.QueueDeclare(
		"admin_queue_doctor"+id,
		false,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the admin queue")

	err = ch.QueueBind(
		q.Name,
		utils.LOGGING_KEY+".*",
		utils.AdministrationExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the admin queue")

	return q.Name
}

func consumeDoctorQueue(ctx context.Context, wg *sync.WaitGroup, ch *amqp.Channel, queueName string) {
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
			log.Println("Stopping consumeDoctorQueue...")
			return
		case d, ok := <-msgs:
			if !ok {
				return
			}
			log.Printf("Received a message from technic: %s", d.Body)
		}
	}
}

func consumeAdminQueue(ctx context.Context, wg *sync.WaitGroup, ch *amqp.Channel, queueName string) {
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
			log.Println("Stopping consumeAdminQueue...")
			return
		case d, ok := <-msgs:
			if !ok {
				return
			}
			log.Printf("Admin message received: %s", d.Body)
		}
	}
}

func publishMessages(ctx context.Context, wg *sync.WaitGroup, ch *amqp.Channel, doctorId string) {
	defer wg.Done()
	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping publishMessages...")
			return
		default:
			randomIndexOp := rand.Intn(len(operations))
			randomIndexMsg := rand.Intn(len(messages))
			randomOperation := operations[randomIndexOp]
			randomName := messages[randomIndexMsg]

			utils.SendMessage(ch, utils.OperationsExchange, randomOperation, randomName+" "+randomOperation, doctorId, true)
			utils.SendMessage(ch, utils.OperationsExchange, utils.LOGGING_KEY, randomName+" "+randomOperation, doctorId, false)
			time.Sleep(2 * time.Second)
		}
	}
}

func manualMessageInput(ctx context.Context, wg *sync.WaitGroup, ch *amqp.Channel, doctorId string) {
	defer wg.Done()
	reader := bufio.NewReader(os.Stdin)
	for {
		select {
		case <-ctx.Done():
			log.Println("Stopping manualMessageInput...")
			return
		default:
			fmt.Print("Enter the surname: ")
			surname, err := reader.ReadString('\n')
			utils.FailOnError(err, "Failed to read from stdin")

			surname = strings.TrimSpace(surname)
			if surname == "" {
				log.Println("Surname cannot be empty. Please enter a valid surname.")
				continue
			}
			operation := ""

			for {
				validInput := true
				fmt.Println("Operation types:")
				fmt.Println("1. Knee")
				fmt.Println("2. Elbow")
				fmt.Println("3. Hip")
				fmt.Print("Enter the type of operation: ")

				number, err := reader.ReadString('\n')
				number = strings.TrimSpace(number)
				utils.FailOnError(err, "Failed to read from stdin")
				switch number {
				case "1":
					operation = "knee"
				case "2":
					operation = "elbow"
				case "3":
					operation = "hip"
				default:
					fmt.Println("Invalid number:", number, ". Please choose 1, 2, or 3.")
					validInput = false
				}
				if validInput {
					break
				}
			}

			message := surname + " " + operation
			utils.SendMessage(ch, utils.OperationsExchange, operation, message, doctorId, true)
			utils.SendMessage(ch, utils.OperationsExchange, utils.LOGGING_KEY+".*", message, doctorId, false)
		}
	}
}
