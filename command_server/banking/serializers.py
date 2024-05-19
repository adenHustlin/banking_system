from rest_framework import serializers

from .models import Account


class TransactionBaseSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    amount = serializers.IntegerField(min_value=1)  # min_value를 1로 설정하여 0 이하 값을 방지
    description = serializers.CharField()


class DepositSerializer(TransactionBaseSerializer):
    pass


class WithdrawSerializer(TransactionBaseSerializer):
    pass
