from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccountViewSet, DepositViewSet, UserViewSet, WithdrawViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"deposit", DepositViewSet, basename="deposit")
router.register(r"withdraw", WithdrawViewSet, basename="withdraw")

urlpatterns = [
    path("", include(router.urls)),
]
