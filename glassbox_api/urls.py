"""glassbox_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from django.contrib.auth import views as auth_views
from rest_framework.permissions import AllowAny
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView,PasswordChangeView
schema_view = get_schema_view(
    title='Glassdoor API',
    description='Your API description',
    version='1.0.0',
    permission_classes=[AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('api.urls')),
    path('api/v1/', include('payment_gateway.urls')),

    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('password_reset/',
         PasswordResetView.as_view(), name='password_reset_confirm'),
    path('password_reset_confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('dj-rest-auth/password/change/',
         PasswordChangeView.as_view(), name='password_reset_confirm'),
    path('openapi/', schema_view, name='openapi-schema'),

]
