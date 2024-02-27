from django.urls import path
from rest_framework.routers import DefaultRouter
from .import views
from .views import VerificationAPIView,ResendVerificationAPIView

router = DefaultRouter()
router.register('registration', views.UserRegistrationViewSet, basename='registration')
router.register('logout', views.UserLogoutViewSet, basename='logout')
router.register('profile', views.UserViewSet, basename='profile')
urlpatterns = [
    path('verify/', VerificationAPIView.as_view(), name='verify'),
    path('resend/', ResendVerificationAPIView.as_view(), name='resend_verification'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-password-reset/', views.VerifyPasswordResetView.as_view(), name='verify_password_reset'),

]

urlpatterns = urlpatterns + router.urls
