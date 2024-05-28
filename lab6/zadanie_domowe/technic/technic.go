package main

import (
	"bufio"
	"fmt"
	"log"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/streadway/amqp"
	utils "rabbit"
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

func sendMessageToDoctor(ch *amqp.Channel, message string, doctorID string) {
	err := ch.Publish(
		"",                       // exchange
		"doctor_queue_"+doctorID, // routing key
		false,                    // mandatory
		false,                    // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(message),
		})
	utils.FailOnError(err, "Failed to send message back to doctor")
	fmt.Println(" [x] Sent message to doctor: ", message)
}

func main() {
	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	utils.FailOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open the channel")
	defer ch.Close()

	operation1, operation2 := readInput()

	// Declare a direct exchange
	err = ch.ExchangeDeclare(
		"operations_exchange", // name
		"direct",              // type
		true,                  // durable
		false,                 // auto-deleted
		false,                 // internal
		false,                 // no-wait
		nil,                   // arguments
	)
	utils.FailOnError(err, "Failed to declare the exchange")

	// Declare two queues
	queue1, err := ch.QueueDeclare(
		string(operation1), // name
		true,               // durable
		false,              // delete when unused
		false,              // exclusive
		false,              // no-wait
		nil,                // arguments
	)
	utils.FailOnError(err, "Failed to declare the queue 1")

	queue2, err := ch.QueueDeclare(
		string(operation2), // name
		true,               // durable
		false,              // delete when unused
		false,              // exclusive
		false,              // no-wait
		nil,                // arguments
	)
	utils.FailOnError(err, "Failed to declare the queue 2")

	// Bind queues to the exchange with routing keys
	err = ch.QueueBind(
		queue1.Name,           // queue name
		string(operation1),    // routing key
		"operations_exchange", // exchange
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the queue 1")

	err = ch.QueueBind(
		queue2.Name,           // queue name
		string(operation2),    // routing key
		"operations_exchange", // exchange
		false,
		nil,
	)
	utils.FailOnError(err, "Failed to bind the queue 2")

	// Create consumers to read messages from the queues
	err = ch.Qos(
		1,     // prefetch count
		0,     // prefetch size
		false, // global
	)
	utils.FailOnError(err, "Failed to set QoS")
	msgs1, err := ch.Consume(
		queue1.Name, // queue
		"",          // consumer
		true,        // auto-ack
		false,       // exclusive
		false,       // no-local
		false,       // no-wait
		nil,         // args
	)
	utils.FailOnError(err, "Failed to register a consumer for queue 1")

	msgs2, err := ch.Consume(
		queue2.Name, // queue
		"",          // consumer
		true,        // auto-ack
		false,       // exclusive
		false,       // no-local
		false,       // no-wait
		nil,         // args
	)
	utils.FailOnError(err, "Failed to register a consumer for queue 2")

	rand.Seed(time.Now().UnixNano())

	var mu sync.Mutex

	processMessage := func(d amqp.Delivery, operation OperationType) {
		mu.Lock()
		defer mu.Unlock()
		log.Printf("Received a message from %s queue: %s", operation, d.Body)
		res := strings.Split(string(d.Body), " ")
		time.Sleep(time.Duration(rand.Intn(10)+1) * time.Second)
		sendMessageToDoctor(ch, res[1]+" "+string(operation)+" DONE", res[0])
	}

	go func() {
		for {
			select {
			case d := <-msgs1:
				processMessage(d, operation1)
			case d := <-msgs2:
				processMessage(d, operation2)
			}
		}
	}()
	// Setup administration exchange and queue
	err = ch.ExchangeDeclare(
		"administration", // name
		"fanout",         // type
		true,             // durable
		false,            // auto-deleted
		false,            // internal
		false,            // no-wait
		nil,              // arguments
	)
	utils.FailOnError(err, "Failed to declare the administration exchange")

	adminQueue, err := ch.QueueDeclare(
		"admin_queue", // name
		false,         // durable
		false,         // delete when unused
		false,         // exclusive
		false,         // no-wait
		nil,           // arguments
	)
	utils.FailOnError(err, "Failed to declare a queue")

	err = ch.QueueBind(
		adminQueue.Name,  // queue name
		"",               // routing key
		"administration", // exchange
		false,            // no-wait
		nil,              // arguments
	)
	utils.FailOnError(err, "Failed to bind a queue")

	go func() {
		//defer wg.Done()
		msgs, err := ch.Consume(
			adminQueue.Name,
			"",
			true,
			false,
			false,
			false,
			nil,
		)
		utils.FailOnError(err, "Failed to register a consumer")

		for d := range msgs {
			log.Printf("Admin message received: %s", d.Body)
		}
	}()
	// Block forever
	select {}
}
