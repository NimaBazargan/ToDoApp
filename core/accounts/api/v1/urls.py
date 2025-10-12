from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = "api-v1"

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("token/login/", views.CustomAuthToken.as_view(), name="token-login"),
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path(
        "change-password/",
        views.ChangePasswordApiView.as_view(),
        name="change-password",
    ),
    path("profile/", views.ProfileApiView.as_view(), name="profile"),
    path(
        "activation/confirm/<str:token>/",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    path(
        "activation/resend/",
        views.ActivationResendApiView.as_view(),
        name="activation-resend",
    ),
    path(
        "reset-password/", views.ResetPasswordApiView.as_view(), name="reset-password"
    ),
    path(
        "reset-password/<str:token>/",
        views.ResetConfirmApiView.as_view(),
        name="reset-password-confirm",
    ),
]
