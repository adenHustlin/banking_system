import threading
from time import sleep

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Account, Transaction


class ConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        self.client1 = APIClient()
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword1"
        )
        self.client1.login(username="testuser1", password="testpassword1")
        self.account1 = Account.objects.create(user=self.user1, balance=1000)

    def test_concurrent_deposit(self):
        """
        동시 입금 테스트:
        - 두 개의 동시 입금 트랜잭션이 올바르게 처리되고, 계좌 잔액이 정확히 업데이트되는지 확인합니다.
        """
        url = reverse("deposit-list")
        data1 = {
            "account": self.account1.id,
            "amount": 500,
            "description": "Concurrent deposit 1",
        }
        data2 = {
            "account": self.account1.id,
            "amount": 300,
            "description": "Concurrent deposit 2",
        }

        def deposit(client, data):
            sleep(0.1)  # 잠시 대기하여 동시성 문제를 유발
            response = client.post(url, data, format="json")
            print(response.data)

        thread1 = threading.Thread(target=deposit, args=(self.client1, data1))
        thread2 = threading.Thread(target=deposit, args=(self.client1, data2))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 1800)  # 1000 + 500 + 300

    def test_concurrent_withdraw(self):
        """
        동시 출금 테스트:
        - 두 개의 동시 출금 트랜잭션이 올바르게 처리되고, 계좌 잔액이 정확히 업데이트되는지 확인합니다.
        """
        url = reverse("withdraw-list")
        data1 = {
            "account": self.account1.id,
            "amount": 500,
            "description": "Concurrent withdraw 1",
        }
        data2 = {
            "account": self.account1.id,
            "amount": 300,
            "description": "Concurrent withdraw 2",
        }

        def withdraw(client, data):
            sleep(0.1)  # 잠시 대기하여 동시성 문제를 유발
            response = client.post(url, data, format="json")
            print(response.data)

        thread1 = threading.Thread(target=withdraw, args=(self.client1, data1))
        thread2 = threading.Thread(target=withdraw, args=(self.client1, data2))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.account1.refresh_from_db()
        self.assertEqual(self.account1.balance, 200)  # 1000 - 500 - 300

    def test_concurrent_withdraw_insufficient_funds(self):
        """
        동시 출금 테스트 (잔액 부족):
        - 두 개의 동시 출금 트랜잭션에서 하나는 성공하고, 다른 하나는 잔액 부족으로 실패하는지 확인합니다.
        """
        url = reverse("withdraw-list")
        data1 = {
            "account": self.account1.id,
            "amount": 800,
            "description": "Concurrent withdraw 1",
        }
        data2 = {
            "account": self.account1.id,
            "amount": 800,
            "description": "Concurrent withdraw 2",
        }

        def withdraw(client, data):
            sleep(0.1)  # 잠시 대기하여 동시성 문제를 유발
            response = client.post(url, data, format="json")
            print(response.data)

        thread1 = threading.Thread(target=withdraw, args=(self.client1, data1))
        thread2 = threading.Thread(target=withdraw, args=(self.client1, data2))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        self.account1.refresh_from_db()
        self.assertTrue(
            self.account1.balance in [200, 0]
        )  # One transaction should succeed, the other should fail

        transactions = Transaction.objects.filter(account=self.account1)
        self.assertEqual(transactions.count(), 1 if self.account1.balance == 200 else 0)
