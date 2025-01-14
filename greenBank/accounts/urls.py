from django.urls import path
from .views import * 


urlpatterns = [
    path("", createAndGetting, name="createAccount"),
    path("<int:accountId>", changeAndGettingAandDelete, name="getAccountById"),
]