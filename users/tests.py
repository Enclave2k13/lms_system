from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course
from users.models import User, Subscription


class UsersEndpointTest(APITestCase):
    """Тесты эндпоинтов пользователей и платежей."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@test.com', password='pass123')

    def test_user_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_create(self):
        response = self.client.post('/api/users/', {'email': 'new@test.com', 'password': 'pass123'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_retrieve(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/users/{self.user.pk}/', {'phone': '123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionEndpointTest(APITestCase):
    """Тесты эндпоинта подписки."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@test.com', password='pass123')
        self.course = Course.objects.create(name='Course', owner=self.user)

    def test_subscribe(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscription/', {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscription/', {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')

    def test_subscribe_unauthenticated(self):
        response = self.client.post('/api/subscription/', {'course_id': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_subscribed_in_course(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/subscription/', {'course_id': self.course.pk})
        response = self.client.get(f'/api/courses/{self.course.pk}/')
        self.assertTrue(response.data['is_subscribed'])
