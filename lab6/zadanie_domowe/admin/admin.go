package main

import (
	"bufio"
	"github.com/streadway/amqp"
	"log"
	"os"
	utils "rabbit"
	"sync"
)

func main() {
	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	utils.FailOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open the channel")
	defer ch.Close()

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

	logQueue, err := ch.QueueDeclare(
		"",    // name
		false, // durable
		false, // delete when unused
		true,  // exclusive
		false, // no-wait
		nil,   // arguments
	)
	utils.FailOnError(err, "Failed to declare a queue")

	err = ch.QueueBind(
		logQueue.Name,    // queue name
		"",               // routing key
		"administration", // exchange
		false,            // no-wait
		nil,              // arguments
	)
	utils.FailOnError(err, "Failed to bind a queue")

	var wg sync.WaitGroup
	wg.Add(2)

	// Read from the adminQueue
	go func() {
		defer wg.Done()
		msgs, err := ch.Consume(
			logQueue.Name,
			"",
			true,
			false,
			false,
			false,
			nil,
		)
		utils.FailOnError(err, "Failed to register a consumer")

		for d := range msgs {
			log.Printf(" [x] %s", d.Body)
		}
	}()

	go func() {
		defer wg.Done()
		reader := bufio.NewReader(os.Stdin)

		for {
			input, err := reader.ReadString('\n')
			utils.FailOnError(err, "Failed to read from stdin")
			err = ch.Publish(
				"administration",
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
		defer wg.Done()
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
	select {}

}
