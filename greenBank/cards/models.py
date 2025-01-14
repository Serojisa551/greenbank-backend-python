from django.db import models
from accounts.models import Accounts


class Cards(models.Model):
    id = models.AutoField(primary_key=True)
    cardName = models.CharField(max_length=50)
    cardNumber = models.CharField(max_length=16, unique=True)
    cardType = models.CharField(max_length=7)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    cardCurrency = models.CharField(max_length=3)
    CVV = models.CharField(max_length=3)
    cardExpirationDate = models.DateField()
    is_deleted = models.BooleanField(default=False)