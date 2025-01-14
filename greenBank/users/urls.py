from django.urls import path
from .views import *


urlpatterns = [
    path('<int:userId>', changeAndGettingAandDelete),
    path("changePassword", changePassword),
    path("imge/<int:ImgId>", getUserImg),
    path("changeEmail", changeEmail),
    path("newEmail", newEmail),
    path("", getAllUsers),
]