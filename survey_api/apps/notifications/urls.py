from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.notifications.views import NotificationListView

# router = DefaultRouter()
# router.register(r'notifications', NotificationListView, basename='notificationsList')

urlpatterns = [
    path(r'notifications', NotificationListView.as_view()),
]