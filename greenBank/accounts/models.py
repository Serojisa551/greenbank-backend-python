from django.db import models


class Accounts(models.Model):
    accountName = models.CharField(max_length=50, unique=False, null=True)
    accountNumber = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default="0.00")
    accountType = models.CharField(max_length=7)
    currency = models.CharField(max_length=3, default="AMD")
    isDefault = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
