from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    path('chats/', include('apps.chats.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('surveys/', include('apps.surveys.urls')),
    path('user-profile/', include('apps.user_profile.urls')),
    path('user/', include('apps.users.urls'))
]