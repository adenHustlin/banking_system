import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Account, Transaction, User
from .producer import send_message


def serialize_instance(instance):
    """
    Django 모델 인스턴스를 JSON 직렬화 가능한 딕셔너리로 변환합니다.
    """
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if isinstance(value, Model):
            value = value.pk  # 외래 키 필드는 기본 키 값으로 변환
        elif hasattr(value, "isoformat"):  # datetime 필드 처리
            value = value.isoformat()
        data[field.name] = value
    return data


@receiver(post_save)
@receiver(post_delete)
def handle_model_change(sender, instance, **kwargs):
    if sender not in [User, Account, Transaction]:
        return

    event = (
        "deleted"
        if kwargs.get("signal") == post_delete
        else ("created" if kwargs.get("created", False) else "updated")
    )

    message = {
        "event": event,
        "app_label": instance._meta.app_label,
        "model": instance._meta.model_name,
        "data": serialize_instance(instance),
    }
    queue_name = f"{instance._meta.app_label}_{instance._meta.model_name}_queue"
    send_message(json.dumps(message, cls=DjangoJSONEncoder), queue=queue_name)
