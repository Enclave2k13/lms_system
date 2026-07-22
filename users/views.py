from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from materials.models import Course
from users.models import User, Payment, Subscription
from users.serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    PaymentSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return UserPublicSerializer
        elif self.action == 'retrieve':
            if self.request.user.is_authenticated and self.request.user == self.get_object():
                return UserSerializer
            return UserPublicSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['payment_date']
    ordering = ['payment_date']

    def get_queryset(self):
        queryset = Payment.objects.all()
        course = self.request.query_params.get('course')
        lesson = self.request.query_params.get('lesson')
        payment_method = self.request.query_params.get('payment_method')

        if course:
            queryset = queryset.filter(paid_course_id=course)
        if lesson:
            queryset = queryset.filter(paid_lesson_id=lesson)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        return queryset


class SubscriptionAPIView(APIView):
    """Эндпоинт для управления подпиской на курс."""

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        return Response({"message": message})
