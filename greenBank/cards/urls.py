from django.urls import path
from .views import *

urlpatterns = [
    path("", createAndGetting),
    path("<int:cardId>", changeAndGettingAandDelete),
]
