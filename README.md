# pipelinepy

This is an OAuth Python client callback for the kafka-python-ng client implementation. It is designed to provide a 
simple and straightforward interface for authenticating Adobe IMS (Identity Management System) users into Kafka.

## Installation

Install pipelinepy using pip:

```bash
pip install pipelinepy
```

## Usage

Pipelinepy is designed to be used with the kafka-python-ng client implementation. 
To use it, you need to create an instance of the `ImsTokenProvider` class and pass it to 
the `sasl_oauth_token_provider` parameter of the Kafka producer and consumer.

```bash
pip install kafka-python-ng pipelinepy
```

```python
#!/usr/bin/env python
import threading, time

from kafka import KafkaConsumer, KafkaProducer
from pipelinepy import ImsTokenProvider


class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = KafkaProducer(bootstrap_servers=['broker1:9092','broker2:9092','broker3:9092'],
                                 sasl_mechanism='OAUTHBEARER',
                                 security_protocol='SASL_SSL',
                                 sasl_oauth_token_provider=ImsTokenProvider())

        while not self.stop_event.is_set():
            producer.send('some_existing_topic', b"Hello, world!")
            producer.send('some_existing_topic', b"Salutare, lume!")
            producer.send('some_existing_topic', b"\xc2\xa1Hola, mundo!")
            time.sleep(1)

        producer.close()


class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=['broker1:9092','broker2:9092','broker3:9092'],
                                 auto_offset_reset='earliest',
                                 group_id='test-cg',
                                 consumer_timeout_ms=1000,
                                 sasl_mechanism='OAUTHBEARER',
                                 security_protocol='SASL_SSL',
                                 sasl_oauth_token_provider=ImsTokenProvider())
        consumer.subscribe(['some_existing_topic'])

        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                if self.stop_event.is_set():
                    break

        consumer.close()


def main():

    tasks = [
        Producer(),
        Consumer()
    ]

    # Start threads of a publisher/producer and a subscriber/consumer to 'my-topic' Kafka topic
    for t in tasks:
        t.start()

    time.sleep(30)

    # Stop threads
    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()


if __name__ == "__main__":
    main()

```

## Environment Variables

The following environment variables need to be set:

- `IMS_URL`: The base URL of the IMS service (does not include the '/ims/token/v1' part).
- `IMS_CLIENT_ID`: The client ID for the IMS service.
- `IMS_CLIENT_SECRET`: The client secret for the IMS service.
- `IMS_CLIENT_CODE`: The client code for the IMS service.

## Contributing

Contributions are welcome. Please submit a pull request or create an issue to discuss the changes you want to make.
