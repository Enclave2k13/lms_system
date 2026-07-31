from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_course_update_email(course_id):
    """Отправляет письмо подписчикам при обновлении курса."""
    from materials.models import Course
    from users.models import Subscription

    course = Course.objects.get(pk=course_id)
    subscriptions = Subscription.objects.filter(course=course).select_related('user')

    for sub in subscriptions:
        send_mail(
            subject=f'Курс "{course.name}" обновлён',
            message=f'Курс "{course.name}" был обновлён!',
            from_email=None,
            recipient_list=[sub.user.email],
            fail_silently=True,
        )
