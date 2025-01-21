from django.urls import path, include
from rest_framework import routers
from .views import UserRegistrationView, UserViewSet

router = routers.DefaultRouter()
router.register('account', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
]