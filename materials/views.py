from rest_framework import viewsets
from rest_framework import generics

from materials.models import Course, Lesson
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций над курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-представление для получения списка и создания уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic-представление для получения, обновления и удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
