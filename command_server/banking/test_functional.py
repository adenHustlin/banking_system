from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Transaction


class BankingAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword1"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword2"
        )
        self.client.login(username="testuser1", password="testpassword1")
        self.account1 = Account.objects.create(user=self.user1, balance=1000)
        self.account2 = Account.objects.create(user=self.user2, balance=2000)

    def test_deposit_by_owner(self):
        url = reverse("deposit-list")
        data = {
            "account": self.account1.id,
            "amount": 500,
            "description": "Test deposit",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 1500)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.amount, 500)
        self.assertEqual(transaction.balance, 1500)
        self.assertEqual(transaction.transaction_type, "deposit")

    def test_deposit_by_non_owner(self):
        url = reverse("deposit-list")
        data = {
            "account": self.account2.id,
            "amount": 500,
            "description": "Test deposit by non-owner",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.account2.refresh_from_db()
        self.assertEqual(self.account2.balance, 2000)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_withdraw_by_owner(self):
        url = reverse("withdraw-list")
        data = {
            "account": self.account1.id,
            "amount": 300,
            "description": "Test withdraw",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 700)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.amount, 300)
        self.assertEqual(transaction.balance, 700)
        self.assertEqual(transaction.transaction_type, "withdraw")

    def test_withdraw_by_non_owner(self):
        url = reverse("withdraw-list")
        data = {
            "account": self.account2.id,
            "amount": 300,
            "description": "Test withdraw by non-owner",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.account2.refresh_from_db()
        self.assertEqual(self.account2.balance, 2000)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_withdraw_insufficient_funds(self):
        url = reverse("withdraw-list")
        data = {
            "account": self.account1.id,
            "amount": 1500,
            "description": "Test insufficient withdraw",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 1000)
        self.assertEqual(Transaction.objects.count(), 0)
