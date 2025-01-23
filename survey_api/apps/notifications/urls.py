from django.urls import path

from api.v1.notifications.views import NotificationListView

# router = DefaultRouter()
# router.register(r'notifications', NotificationListView, basename='notificationsList')

urlpatterns = [
    path(r"notifications", NotificationListView.as_view()),
]
