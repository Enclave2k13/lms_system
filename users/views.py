from rest_framework import viewsets, filters

from users.models import User, Payment
from users.serializers import UserSerializer, PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


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
