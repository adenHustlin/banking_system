from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet

router = DefaultRouter()
router.register(r"banking", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
]
