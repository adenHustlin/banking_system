import os
import sys

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Account, Transaction, User
from .producer import send_message


def serialize_instance(instance):
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if hasattr(value, "isoformat"):  # handle datetime fields
            value = value.isoformat()
        elif hasattr(value, "pk"):
            value = value.pk
        data[field.name] = value
    return data


@receiver(post_save)
@receiver(post_delete)
def handle_model_change(sender, instance, **kwargs):
    if sender not in [User, Account, Transaction]:
        return
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    event = (
        "deleted"
        if kwargs.get("signal") == post_delete
        else ("created" if kwargs.get("created", False) else "updated")
    )

    message = {
        "event": event,
        "app_label": app_label,
        "model": model_name,
        "data": serialize_instance(instance),
    }
    queue_name = f"{app_label}_{model_name}_queue"
    send_message(message, queue=queue_name)
