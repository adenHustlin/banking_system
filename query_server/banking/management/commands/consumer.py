import json

import pika
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand

User = get_user_model()


def handle_message(message):
    app_label = message["app_label"]
    model_name = message["model"]
    event = message["event"]
    data = message["data"]

    model = apps.get_model(app_label, model_name)

    # Redis 캐시 무효화
    cache.delete_pattern(f"transaction*")

    if model_name == "account" and "user" in data:
        data["user"] = User.objects.get(pk=data["user"])

    if model_name == "transaction" and "account" in data:
        from banking.models import Account

        data["account"] = Account.objects.get(pk=data["account"])

    if model_name == "transaction" and "user" in data:
        data["user"] = User.objects.get(pk=data["user"])

    if event == "created":
        model.objects.create(**data)
    elif event == "updated":
        instance = model.objects.get(pk=data["id"])
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()
    elif event == "deleted":
        model.objects.filter(pk=data["id"]).delete()


class Command(BaseCommand):
    help = "Run RabbitMQ consumer"

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(settings.RABBITMQ_HOST)
        )
        channel = connection.channel()

        def callback(ch, method, properties, body):
            message = json.loads(body)
            handle_message(message)

        queues = [
            "auth_user_queue",
            "banking_account_queue",
            "banking_transaction_queue",
        ]
        for queue in queues:
            channel.basic_consume(
                queue=queue, on_message_callback=callback, auto_ack=True
            )

        print("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
