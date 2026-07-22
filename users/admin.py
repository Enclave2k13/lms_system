from django.contrib import admin

from users.models import User, Payment, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели пользователя."""

    list_display = ('email', 'phone', 'city', 'is_active', 'is_staff')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка для модели платежа."""

    list_display = ('user', 'course', 'status', 'created_at', 'payment_id')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели подписки."""

    list_display = ('user', 'course')
