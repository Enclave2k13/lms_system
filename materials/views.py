from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций над курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return [permission() for permission in self.permission_classes]
