import os

from django.contrib.auth.models import User
from django.test import TestCase

from command_server.banking.models import Account, Transaction


class AccountModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["ENABLE_MQ"] = "false"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        os.environ["ENABLE_MQ"] = "true"

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.account = Account.objects.create(user=self.user, balance=1000)

    def test_account_creation(self):
        self.assertEqual(self.account.user.username, "testuser")
        self.assertEqual(self.account.balance, 1000)

    def test_deposit_transaction(self):
        transaction = Transaction.objects.create(
            account=self.account,
            user=self.user,
            amount=500,
            balance=self.account.balance + 500,
            transaction_type="deposit",
            description="Test deposit",
        )
        self.account.balance += 500
        self.account.save()
        self.assertEqual(transaction.balance, 1500)
        self.assertEqual(self.account.balance, 1500)

    def test_withdraw_transaction(self):
        transaction = Transaction.objects.create(
            account=self.account,
            user=self.user,
            amount=300,
            balance=self.account.balance - 300,
            transaction_type="withdraw",
            description="Test withdraw",
        )
        self.account.balance -= 300
        self.account.save()
        self.assertEqual(transaction.balance, 700)
        self.assertEqual(self.account.balance, 700)
