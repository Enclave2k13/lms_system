from urllib.parse import urlparse

from rest_framework.serializers import ValidationError


class YouTubeURLValidator:
    """Валидатор: разрешает только ссылки на youtube.com."""

    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)
        if value:
            parsed = urlparse(value)
            host = parsed.netloc.lower()
            if host != 'youtube.com' and host != 'www.youtube.com':
                raise ValidationError('Разрешены только ссылки на youtube.com')
