from django.urls import path
from .views import *

urlpatterns = [
    path("", transaction),
    path("QR", createQRToken),
    path("filter", getHistory)
]