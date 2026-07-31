from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson
from materials.paginators import MaterialsPagination
from materials.serializers import CourseSerializer, LessonSerializer
from materials.tasks import send_course_update_email
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций над курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.instance
        last_updated_at = course.updated_at
        serializer.save()

        # Уведомление отправляется, только если курс не обновлялся более 4 часов
        if timezone.now() - last_updated_at < timedelta(hours=4):
            return
        send_course_update_email.delay(course.pk)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-представление для получения списка и создания уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic-представление для получения, обновления и удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):
        lesson = serializer.instance
        course = lesson.course
        last_updated_at = course.updated_at
        serializer.save()

        # Обновление урока считается обновлением курса
        Course.objects.filter(pk=course.pk).update(updated_at=timezone.now())

        # Уведомление отправляется, только если курс не обновлялся более 4 часов
        if timezone.now() - last_updated_at < timedelta(hours=4):
            return
        send_course_update_email.delay(course.pk)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]
