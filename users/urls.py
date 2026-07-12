from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
