from django.core.cache import cache
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets

from .models import Transaction
from .pagination import CursorOrPageNumberPagination
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    pagination_class = CursorOrPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve a list of transactions",
        manual_parameters=[
            openapi.Parameter(
                "account_id",
                openapi.IN_QUERY,
                description="Account ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "transaction_type",
                openapi.IN_QUERY,
                description="Transaction Type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start Date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End Date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Ordering field (e.g., transaction_date or -transaction_date)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Page size",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get_queryset(self):
        # swagger_fake_view 체크
        if getattr(self, "swagger_fake_view", False):
            return Transaction.objects.none()

        user = self.request.user
        account_id = self.request.query_params.get("account_id")
        transaction_type = self.request.query_params.get("transaction_type")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        ordering = self.request.query_params.get("ordering", "transaction_date")

        # 캐시 키 생성 (O(1) 상수 시간 복잡도)
        cache_key = f"transaction_{user.id}_{account_id}_{transaction_type}_{start_date}_{end_date}_{ordering}"

        # 캐시에서 쿼리셋 가져오기 시도 (O(1) 상수 시간 복잡도)
        cached_queryset = cache.get(cache_key)
        if cached_queryset is not None:
            return cached_queryset

        # 쿼리셋 필터링 (여러 필터 적용, 대부분 O(n))
        queryset = Transaction.objects.filter(account__user=user)

        # account_id 필터 적용 (O(1) 상수 시간 복잡도, 외래 키 인덱스 있음)
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        # transaction_type 필터 적용 (O(1) 상수 시간 복잡도, 인덱스 있음)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        # 날짜 범위 필터 적용 (O(log n) 로그 시간 복잡도, 날짜 인덱스 있음)
        if start_date and end_date:
            queryset = queryset.filter(transaction_date__range=[start_date, end_date])

        # 정렬 적용 (O(n log n))
        queryset = queryset.order_by(ordering)

        # 필터링된 쿼리셋 캐시에 저장 (O(1) 상수 시간 복잡도)
        cache.set(cache_key, queryset, timeout=60 * 60)  # 1시간 동안 캐싱

        # 최종 쿼리셋 반환 (O(n))
        return queryset
