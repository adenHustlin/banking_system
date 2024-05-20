from django.contrib.auth.models import User
from django.db import OperationalError, transaction
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Account, Transaction
from .serializers import (
    AccountSerializer,
    DepositSerializer,
    UserSerializer,
    WithdrawSerializer,
)
from .utils import retry


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]


class DepositViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @retry(OperationalError, tries=5, delay=1, backoff=2)
    def create(self, request):
        """
        입금 기능을 처리하는 메소드입니다.

        시간 복잡도 분석:
        - 데이터 검증 (serializer.is_valid()): O(n)
        - 데이터베이스 조회 (account 조회): O(1)
        - 계좌 소유주 확인: O(1)
        - 데이터베이스 업데이트 (account.save()): O(1)
        - 트랜잭션 생성 (Transaction.objects.create()): O(1)
        - 응답 생성: O(1)

        전체 시간 복잡도: O(1)
        """
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.validated_data["account"]
            # 계좌 소유주 확인
            if account.user != request.user:
                return Response(
                    {"error": "You do not own this account"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            amount = serializer.validated_data["amount"]
            description = serializer.validated_data["description"]

            with transaction.atomic():
                # 계좌 레코드 잠금 및 잔액 업데이트
                account = (
                    Account.objects.select_for_update()
                    .only("id", "balance")
                    .get(id=account.id)
                )
                account.balance += amount
                account.save()  # 데이터베이스 업데이트 (O(1))

                # 트랜잭션 생성
                Transaction.objects.create(
                    account=account,
                    user=request.user,
                    amount=amount,
                    balance=account.balance,
                    transaction_type="deposit",
                    description=description,
                )  # 트랜잭션 생성 (O(1))

            return Response(
                {"status": "deposit successful"}, status=status.HTTP_201_CREATED
            )  # 응답 생성 (O(1))

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # 응답 생성 (O(1))


class WithdrawViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @retry(OperationalError, tries=5, delay=1, backoff=2)
    def create(self, request):
        """
        출금 기능을 처리하는 메소드입니다.

        시간 복잡도 분석:
        - 데이터 검증 (serializer.is_valid()): O(1)
        - 데이터베이스 조회 (account 조회): O(1)
        - 계좌 소유주 확인: O(1)
        - 잔액 확인: O(1)
        - 데이터베이스 업데이트 (account.save()): O(1)
        - 트랜잭션 생성 (Transaction.objects.create()): O(1)
        - 응답 생성: O(1)

        전체 시간 복잡도: O(1)
        """
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.validated_data["account"]
            # 계좌 소유주 확인
            if account.user != request.user:
                return Response(
                    {"error": "You do not own this account"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            amount = serializer.validated_data["amount"]
            description = serializer.validated_data["description"]

            with transaction.atomic():
                # 잔액 확인 및 레코드 잠금
                account = (
                    Account.objects.select_for_update()
                    .only("id", "balance")
                    .get(id=account.id)
                )
                if account.balance < amount:
                    return Response(
                        {"error": "Insufficient funds"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # 계좌 잔액 업데이트
                account.balance -= amount
                account.save()  # 데이터베이스 업데이트 (O(1))

                # 트랜잭션 생성
                Transaction.objects.create(
                    account=account,
                    user=request.user,
                    amount=amount,
                    balance=account.balance,
                    transaction_type="withdraw",
                    description=description,
                )  # 트랜잭션 생성 (O(1))

            return Response(
                {"status": "withdraw successful"}, status=status.HTTP_201_CREATED
            )  # 응답 생성 (O(1))

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # 응답 생성 (O(1))
