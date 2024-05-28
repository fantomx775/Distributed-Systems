package main

import (
	"github.com/streadway/amqp"
	"log"
	"strconv"
	"sync"
	"time"
)

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func sendMessage(ch *amqp.Channel, exchange string, key string, body string) {
	err := ch.Publish(
		exchange, // exchange
		key,      // routing key
		false,    // mandatory
		false,    // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
		})
	failOnError(err, "Failed to publish a message")
	log.Printf(" [x] Sent %s", body)
}

func main() {
	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	failOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	defer ch.Close()

	err = ch.ExchangeDeclare(
		"operations_exchange", // name
		"direct",              // type
		true,                  // durable
		false,                 // auto-deleted
		false,                 // internal
		false,                 // no-wait
		nil,                   // arguments
	)
	failOnError(err, "Failed to declare the exchange")

	doctorID := "doctor1"
	doctorQueueName := "doctor_queue_" + doctorID
	q, err := ch.QueueDeclare(
		doctorQueueName,
		false,
		false,
		false,
		false,
		nil,
	)
	failOnError(err, "Failed to declare a queue")

	var wg sync.WaitGroup
	wg.Add(3) // Add 2 because we have 2 goroutines

	go func() {
		defer wg.Done()
		msgs, err := ch.Consume(
			q.Name, // queue
			"",     // consumer
			true,   // auto-ack
			false,  // exclusive
			false,  // no-local
			false,  // no-wait
			nil,    // args
		)
		failOnError(err, "Failed to register a consumer")
		log.Println("Receiving")

		for d := range msgs {
			log.Printf("Received a message: %s", d.Body)
		}
	}()

	// operations := []string{"knee", "elbow", "hip"}
	operations := []string{"knee"}

	messages := []string{
		doctorID + " Kowalski",
		// doctorID + " Nowak",
		// doctorID + " Chujak",
	}
	number := 0
	go func() {
		defer wg.Done()
		for {
			for i, op := range operations {
				number++
				sendMessage(ch, "operations_exchange", op, messages[i]+strconv.Itoa(number))
			}
			time.Sleep(10 * time.Second)
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
	failOnError(err, "Failed to declare the administration exchange")

	adminQueue, err := ch.QueueDeclare(
		"admin_queue", // name
		false,         // durable
		false,         // delete when unused
		false,         // exclusive
		false,         // no-wait
		nil,           // arguments
	)
	failOnError(err, "Failed to declare a queue")

	err = ch.QueueBind(
		adminQueue.Name,  // queue name
		"",               // routing key
		"administration", // exchange
		false,            // no-wait
		nil,              // arguments
	)
	failOnError(err, "Failed to bind a queue")

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
		failOnError(err, "Failed to register a consumer")

		for d := range msgs {
			log.Printf("Admin message received: %s", d.Body)
		}
	}()

	wg.Wait() // Wait for all goroutines to finish
}
