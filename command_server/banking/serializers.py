from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "balance", "user"]

    def create(self, validated_data):
        account = Account.objects.create(
            user=validated_data["user"], balance=validated_data["balance"]
        )
        return account


class TransactionBaseSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    amount = serializers.IntegerField(min_value=1)  # min_value를 1로 설정하여 0 이하 값을 방지
    description = serializers.CharField()


class DepositSerializer(TransactionBaseSerializer):
    pass


class WithdrawSerializer(TransactionBaseSerializer):
    pass
