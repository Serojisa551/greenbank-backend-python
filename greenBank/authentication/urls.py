from django.urls import path
from .views import *

urlpatterns = [
    path("registration", register_user),
    path("login", login_user),
    path("logout", logout_user),
    path("refresh", refresh),
    path("verifyNumber", checkActiveCcode),
    path("resetVerifyNumber/<int:userId>", refreshActivationCode),
    path("forgetPassword", forgetPassword),
    path("resetPassword", resetPassword),
]
