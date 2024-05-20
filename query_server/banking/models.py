from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    balance = models.PositiveBigIntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
    ]

    transaction_date = models.DateTimeField()
    amount = models.PositiveBigIntegerField()
    balance = models.PositiveBigIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField()

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["transaction_date", "transaction_type"]),
        ]
