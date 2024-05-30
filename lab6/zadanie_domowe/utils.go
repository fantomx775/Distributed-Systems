package utils

import (
	"github.com/streadway/amqp"
	"log"
)

const (
	RabbitMQURL                = "amqp://guest:guest@localhost:5672/"
	OperationsExchange         = "operations_exchange"
	OperationsExchangeType     = "direct"
	AdministrationExchange     = "administration"
	AdministrationExchangeType = "fanout"
	LOGGING_KEY                = "logging"
)

func FailOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func SendMessage(ch *amqp.Channel, exchange string, key string, body string, id string, logging bool) {
	err := ch.Publish(
		exchange, // exchange
		key,      // routing key
		false,    // mandatory
		false,    // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
			ReplyTo:     id,
		})
	FailOnError(err, "Failed to publish a message")
	if logging {
		log.Printf(" [x] Sent %s", body)
	}
}
