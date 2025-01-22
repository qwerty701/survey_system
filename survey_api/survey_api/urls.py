from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


jwt_authentication = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Введите JWT токен в формате 'Bearer <токен>'",
    type=openapi.TYPE_STRING,
)


schema_view = get_schema_view(
    openapi.Info(
        title="Survey API",
        default_version='v1',
        description="Документация для API опросов",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@surveyapi.local"),
        license=openapi.License(name="BSD License"),
        security=[jwt_authentication]
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
    path('api/v1/', include('api.v1.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]