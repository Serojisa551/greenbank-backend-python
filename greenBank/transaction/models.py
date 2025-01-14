from django.db import models
from authentication.models import Users


class Transactions(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    sender = models.CharField(max_length=20)
    receiver = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=20)
    date = models.DateField()
    is_successful = models.BooleanField(default=False)
