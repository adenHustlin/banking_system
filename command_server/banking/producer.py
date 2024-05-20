import json

import pika
from django.conf import settings


def send_message(message, queue):
    if not settings.ENABLE_MQ:
        return
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(settings.RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange="", routing_key=queue, body=message)
    connection.close()
