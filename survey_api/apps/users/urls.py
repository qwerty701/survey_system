from django.urls import include, path
from rest_framework import routers

from api.v1.users.views import UserRegistrationView, UserViewSet

router = routers.DefaultRouter()
router.register("account", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
]
