from django.urls import path
from .views import * 

urlpatterns = [
    path("USD", getUSD),
    path("RUB", getRUB),
    path("EUR", getEUR),
    path("AMD", getAMD),
    path("", getAll),
]

