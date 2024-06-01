package main

import (
	"bufio"
	"fmt"
	"github.com/google/uuid"
	"github.com/streadway/amqp"
	"log"
	"math/rand"
	"os"
	utils "rabbit"
	"strconv"
	"strings"
	"sync"
	"time"
)

type OperationType string

const (
	Knee  OperationType = "knee"
	Elbow OperationType = "elbow"
	Hip   OperationType = "hip"
)

func readInput() (OperationType, OperationType) {
	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Println("Type 2 different numbers (separated by space) to choose operations for this technic:")
		fmt.Println("1. Knee")
		fmt.Println("2. Elbow")
		fmt.Println("3. Hip")

		input, err := reader.ReadString('\n')
		utils.FailOnError(err, "Failed to read from stdin")

		input = strings.TrimSpace(input)
		parts := strings.Split(input, " ")
		if len(parts) != 2 {
			fmt.Println("Please enter exactly 2 different numbers separated by space.")
			continue
		}

		num1, err1 := strconv.Atoi(parts[0])
		num2, err2 := strconv.Atoi(parts[1])

		if err1 != nil || err2 != nil {
			fmt.Println("Both inputs must be valid numbers.")
			continue
		}

		if num1 == num2 {
			fmt.Println("Please enter two different numbers.")
			continue
		}

		operations := make([]OperationType, 0, 2)
		validInput := true

		for _, number := range []int{num1, num2} {
			switch number {
			case 1:
				operations = append(operations, Knee)
			case 2:
				operations = append(operations, Elbow)
			case 3:
				operations = append(operations, Hip)
			default:
				fmt.Println("Invalid number:", number, ". Please choose 1, 2, or 3.")
				validInput = false
			}
		}

		if validInput {
			fmt.Println("You chose the following operations:")
			for _, operation := range operations {
				fmt.Println(operation)
			}
			return operations[0], operations[1]
		}
	}
}

func main() {
	technicId := uuid.New().String()

	conn, err := amqp.Dial(utils.RabbitMQURL)
	utils.FailOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open the channel")
	defer ch.Close()

	operation1, operation2 := readInput()

	setupExchanges(ch)
	queue1 := setupQueue(ch, operation1)
	queue2 := setupQueue(ch, operation2)
	bindQueue(ch, queue1, operation1)
	bindQueue(ch, queue2, operation2)

	setQoS(ch)

	msgs1 := consumeQueue(ch, queue1)
	msgs2 := consumeQueue(ch, queue2)

	rand.Seed(time.Now().UnixNano())
	var mu sync.Mutex

	go processMessages(msgs1, operation1, technicId, ch, &mu)
	go processMessages(msgs2, operation2, technicId, ch, &mu)

	setupAdminExchange(ch)
	adminQueue := setupAdminQueue(ch)
	go consumeAdminQueue(ch, adminQueue)

	select {}
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
}

func setupQueue(ch *amqp.Channel, operation OperationType) amqp.Queue {
	queue, err := ch.QueueDeclare(
		string(operation),
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the queue")
	return queue
}

func bindQueue(ch *amqp.Channel, queue amqp.Queue, operation OperationType) {
	err := ch.QueueBind(
		queue.Name,
		string(operation),
		utils.OperationsExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the queue")
}

func setQoS(ch *amqp.Channel) {
	err := ch.Qos(
		1,
		0,
		false,
	)
	utils.FailOnError(err, "Failed to set QoS")
}

func consumeQueue(ch *amqp.Channel, queue amqp.Queue) <-chan amqp.Delivery {
	msgs, err := ch.Consume(
		queue.Name,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to register a consumer")
	return msgs
}

func processMessages(msgs <-chan amqp.Delivery, operation OperationType, technicId string, ch *amqp.Channel, mu *sync.Mutex) {
	for d := range msgs {
		mu.Lock()
		log.Printf("Received a message: %s", d.Body)
		//time.Sleep(time.Duration(rand.Intn(10)+1) * time.Second)
		time.Sleep(20 * time.Second)
		utils.SendMessage(ch, utils.OperationsExchange, d.ReplyTo, string(d.Body)+" DONE", technicId, true)
		utils.SendMessage(ch, utils.OperationsExchange, utils.LOGGING_KEY, string(d.Body)+" DONE", technicId, false)
		d.Ack(false)
		mu.Unlock()
	}
}

func setupAdminExchange(ch *amqp.Channel) {
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
}

func setupAdminQueue(ch *amqp.Channel) amqp.Queue {
	adminQueue, err := ch.QueueDeclare(
		"admin_queue_technic",
		false,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to declare the admin queue")
	err = ch.QueueBind(
		adminQueue.Name,
		"",
		utils.AdministrationExchange,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the admin queue")
	return adminQueue
}

func consumeAdminQueue(ch *amqp.Channel, adminQueue amqp.Queue) {
	msgs, err := ch.Consume(
		adminQueue.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to register a consumer for admin queue")

	for d := range msgs {
		log.Printf("Admin message received: %s", d.Body)
	}
}
