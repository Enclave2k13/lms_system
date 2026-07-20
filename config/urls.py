from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    """Главная страница с информацией о проекте и списком эндпоинтов."""

    endpoints = [
        {
            'path': '/api/users/',
            'methods_list': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'description': 'Управление пользователями',
        },
        {
            'path': '/api/courses/',
            'methods_list': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'description': 'Управление курсами',
        },
        {
            'path': '/api/lessons/',
            'methods_list': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'description': 'Управление уроками',
        },
        {
            'path': '/api/payments/',
            'methods_list': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'description': 'Управление платежами (с фильтрацией и сортировкой)',
        },
        {
            'path': '/api/token/',
            'methods_list': ['POST'],
            'description': 'JWT получение пары access/refresh токенов',
        },
        {
            'path': '/api/token/refresh/',
            'methods_list': ['POST'],
            'description': 'JWT обновление access токена',
        },
        {
            'path': '/admin/',
            'methods_list': ['GET', 'POST'],
            'description': 'Админ-панель Django',
        },
    ]

    context = {
        'title': 'LMS System (Online Learning Platform)',
        'version': '1.0.0',
        'description': 'API для платформы онлайн-обучения',
        'endpoints': endpoints,
    }

    return render(request, 'home.html', context)


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('materials.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
