from django.contrib import admin

from users.models import User, Payment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели пользователя."""

    list_display = ('email', 'phone', 'city', 'is_active', 'is_staff')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админка для модели платежа."""

    list_display = ('user', 'amount', 'payment_method', 'payment_date', 'paid_course', 'paid_lesson')
