from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course, Lesson
from users.models import User


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
