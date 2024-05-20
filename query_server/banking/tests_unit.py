from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Transaction


class TransactionViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 유저 생성
        cls.user = User.objects.create_user(username="testuser", password="testpass")

        # 계정 생성
        cls.account = Account.objects.create(user=cls.user, balance=10000)

        # 1000개의 거래내역 생성
        for i in range(1000):
            Transaction.objects.create(
                transaction_date=datetime.now() - timedelta(days=i),
                amount=100 + i,
                balance=10000 - i,
                transaction_type="DEPOSIT" if i % 2 == 0 else "WITHDRAWAL",
                description=f"Transaction {i}",
                account=cls.account,
                user=cls.user,
            )

    def setUp(self):
        self.client.login(username="testuser", password="testpass")

    def test_transaction_list_default(self):
        url = reverse("transaction-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)  # 기본 페이지 사이즈는 10

    def test_transaction_filter_by_account_id(self):
        url = reverse("transaction-list")
        response = self.client.get(url, {"account_id": self.account.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)

    def test_transaction_filter_by_transaction_type(self):
        url = reverse("transaction-list")
        response = self.client.get(url, {"transaction_type": "DEPOSIT"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(t["transaction_type"] == "DEPOSIT" for t in response.data["results"])
        )

    def test_transaction_filter_by_date_range(self):
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        url = reverse("transaction-list")
        response = self.client.get(
            url, {"start_date": start_date, "end_date": end_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["results"]) > 0)

    def test_transaction_ordering(self):
        url = reverse("transaction-list")
        response = self.client.get(url, {"ordering": "-transaction_date"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [t["transaction_date"] for t in response.data["results"]]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_cursor_pagination(self):
        url = reverse("transaction-list")
        response = self.client.get(url, {"page_size": 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 20)

    def test_offset_pagination(self):
        url = reverse("transaction-list")
        response = self.client.get(url, {"page": 2, "page_size": 20})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 20)
