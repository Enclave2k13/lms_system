from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def block_inactive_users():
    """Блокирует пользователей, не заходивших более 30 дней."""
    from users.models import User

    threshold = timezone.now() - timedelta(days=30)
    updated = User.objects.filter(last_login__lt=threshold, is_active=True).update(is_active=False)
    return f'Заблокировано {updated} пользователей'
