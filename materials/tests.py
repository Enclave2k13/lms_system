from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course, Lesson
from materials.tasks import send_course_update_email
from users.models import User, Subscription


class MaterialsEndpointTest(APITestCase):
    """Тесты эндпоинтов курсов и уроков."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email='owner@test.com', password='pass123')
        self.other = User.objects.create_user(email='other@test.com', password='pass123')
        self.moderator = User.objects.create_user(email='mod@test.com', password='pass123')
        mod_group = Group.objects.create(name='moderators')
        self.moderator.groups.add(mod_group)
        self.course = Course.objects.create(name='Course 1', owner=self.owner)
        self.lesson = Lesson.objects.create(
            name='Lesson 1', course=self.course, owner=self.owner,
            video_link='https://www.youtube.com/watch?v=1',
        )

    def test_course_list(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/courses/', {'name': 'New'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_retrieve(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/courses/{self.course.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/courses/{self.course.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_moderator_cant_create(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post('/api/courses/', {'name': 'Mod'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_list(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_create_youtube_ok(self):
        self.client.force_authenticate(user=self.owner)
        data = {'name': 'YT', 'course': self.course.pk, 'video_link': 'https://youtube.com/watch?v=1'}
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_bad_url_rejected(self):
        self.client.force_authenticate(user=self.owner)
        data = {'name': 'Bad', 'course': self.course.pk, 'video_link': 'https://udemy.com/course/1'}
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_retrieve(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_other_user_cant_delete(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_blocked(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseUpdateNotificationTest(APITestCase):
    """Тесты отправки уведомлений об обновлении курса."""

    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email='owner@test.com', password='pass123')
        self.subscriber = User.objects.create_user(email='sub@test.com', password='pass123')
        self.course = Course.objects.create(name='Course', owner=self.owner)
        self.lesson = Lesson.objects.create(
            name='Lesson', course=self.course, owner=self.owner,
            video_link='https://www.youtube.com/watch?v=1',
        )
        Subscription.objects.create(user=self.subscriber, course=self.course)

    def test_course_update_dispatches_email_when_updated_long_ago(self):
        Course.objects.filter(pk=self.course.pk).update(updated_at=timezone.now() - timedelta(hours=5))
        self.client.force_authenticate(user=self.owner)
        with patch('materials.views.send_course_update_email.delay') as mock_delay:
            response = self.client.patch(f'/api/courses/{self.course.pk}/', {'name': 'New name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_called_once_with(self.course.pk)

    def test_course_update_no_email_when_recently_updated(self):
        Course.objects.filter(pk=self.course.pk).update(updated_at=timezone.now() - timedelta(hours=2))
        self.client.force_authenticate(user=self.owner)
        with patch('materials.views.send_course_update_email.delay') as mock_delay:
            response = self.client.patch(f'/api/courses/{self.course.pk}/', {'name': 'New name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_not_called()

    def test_lesson_update_dispatches_email_and_bumps_course(self):
        Course.objects.filter(pk=self.course.pk).update(updated_at=timezone.now() - timedelta(hours=5))
        self.client.force_authenticate(user=self.owner)
        with patch('materials.views.send_course_update_email.delay') as mock_delay:
            response = self.client.patch(f'/api/lessons/{self.lesson.pk}/', {'name': 'Updated lesson'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_called_once_with(self.course.pk)
        self.course.refresh_from_db()
        self.assertLess(timezone.now() - self.course.updated_at, timedelta(minutes=1))

    def test_lesson_update_no_email_within_4_hours(self):
        self.client.force_authenticate(user=self.owner)
        with patch('materials.views.send_course_update_email.delay') as mock_delay:
            response = self.client.patch(f'/api/lessons/{self.lesson.pk}/', {'name': 'Updated lesson'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delay.assert_not_called()

    def test_send_course_update_email_sends_to_subscribers(self):
        from django.core import mail
        send_course_update_email(self.course.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.subscriber.email, mail.outbox[0].to)
