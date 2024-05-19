from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError


class Account(models.Model):
    balance = models.PositiveBigIntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)


class Transaction(models.Model):
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    balance = models.PositiveBigIntegerField()
    transaction_type = models.CharField(max_length=10)
    description = models.TextField()

    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount must be greater than zero")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
