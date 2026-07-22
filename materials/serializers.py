from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import YouTubeURLValidator
from users.models import Subscription


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели урока."""

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [YouTubeURLValidator(field='video_link')]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели курса. Включает уроки, их количество и признак подписки."""

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, course=obj).exists()
