from django.urls import path
from .views import (
    UserInfoView,
    RegistrationView,
    LoginView,
    LogoutView,
    CookieTokenRefreshView,
    ResetPasswordView,
    UploadProfileImageView,
    IsAuthView
)
from .email_views import send_verify_otp, verify_email,send_reset_password_otp

urlpatterns = [
    path("user-info", UserInfoView.as_view(), name="user-info"),
    path("register", RegistrationView.as_view(), name="register-user"),
    path("login", LoginView.as_view(), name="user-login"),
    path("logout", LogoutView.as_view(), name="user-logout"),
    path("refresh", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("send-verify-otp", send_verify_otp, name="send-verify-otp"),
    path("verify-account", verify_email, name="verify-account"),
    path("send-reset-otp",send_reset_password_otp,name="send-reset-password-otp"),
    path("reset-password",ResetPasswordView.as_view(),name="reset-password"),
    path('upload-img',UploadProfileImageView.as_view(),name="upload-profile-image"),
    path('is-auth',IsAuthView.as_view(),name="is-auth"),
]

