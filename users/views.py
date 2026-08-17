import stripe
from rest_framework import viewsets, filters, status
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
from users.services import create_stripe_product, create_stripe_price, create_checkout_session


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
    """ViewSet для просмотра платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = Payment.objects.all()
        course = self.request.query_params.get('course')
        if course:
            queryset = queryset.filter(course_id=course)
        return queryset


class PaymentCreateView(APIView):
    """Создание платежа через Stripe."""

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')
        course = get_object_or_404(Course, pk=course_id)

        try:
            product_id = create_stripe_product(course)
            price_id = create_stripe_price(product_id, course.price)
            session = create_checkout_session(
                price_id,
                success_url='http://localhost:8000/success/',
                cancel_url='http://localhost:8000/cancel/',
            )
        except stripe.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            user=user,
            course=course,
            payment_id=session.id,
            price_id=price_id,
            payment_url=session.url,
            status='pending',
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


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
