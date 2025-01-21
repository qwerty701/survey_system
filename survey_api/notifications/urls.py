from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationListView

router = DefaultRouter()
router.register(r'notifications', NotificationListView)

urlpatterns = [
    path('', include(router.urls)),
]