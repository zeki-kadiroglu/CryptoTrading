import json
import os
import sys

import pika.exceptions
os.path.join(os.path.dirname(__file__), '../')
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from fastapi import WebSocket
import pika
from pika.exchange_type import ExchangeType
import logging

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger("myapp")

class MessageBroker:
    PORT = 5672
    RABBITMQ_HOST = '127.0.0.1'
    USER_NAME = 'guest'
    PASSWORD = 'guest'
    
    def __init__(self) -> None:
        
        # PUB/SUB MESSAGE QUEUE
        
        try: 
            # creds
            self.credentials = pika.PlainCredentials(self.USER_NAME, self.PASSWORD)        
            # Perform connection
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    heartbeat=600,
                    blocked_connection_timeout=300,
                    retry_delay=5, # retry delay in seconds
                    host=self.RABBITMQ_HOST,
                    port=self.PORT,
                    credentials=self.credentials
                    )
                )
            
            # Creating a channel
            self.channel = self.connection.channel()
        except pika.exceptions.ConnectionClosedByBroker as err:
            logger.error(err)
        # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:                
            logger.error(err)
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError as err:
            # print("Connection was closed, retrying...")
            logger.error(err)
                

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        message = body.decode('utf-8')
            
    def publish_socket_message(self, body):
        channel = self.connection.channel()
        
        channel.exchange_declare(
        exchange='socket', exchange_type=ExchangeType.fanout
        )
        channel.basic_publish(
            body=json.dumps(body),
            routing_key = '',
            exchange = 'socket'         
        )
        self.connection.close()
        
    
    def consume_socket_message(self):
        channel = self.connection.channel()
        # Set the prefetch count to 1 to ensure fair dispatch
        channel.basic_qos(prefetch_count=1)
        channel.exchange_declare(
            exchange='socket',
            exchange_type=ExchangeType.fanout
            )
        # Binding the queue to the exchange
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        channel.queue_bind(
            queue=queue_name,
            exchange='socket'
            )
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.callback,
            auto_ack=True,
            )
        self.channel.start_consuming()
            
        
    
