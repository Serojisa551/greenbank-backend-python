from accounts.models import Accounts
from cards.models import Cards
from djongo import models


class Users(models.Model):
    email = models.EmailField()
    password = models.TextField()
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, unique=True)
    img = models.ImageField(upload_to="img/%Y/%m/%d/", null=True, blank=True)
    birthday = models.DateField()
    activationCode = models.CharField(max_length=4)
    expirationActivationCode = models.DateTimeField()
    email_details = models.JSONField(default=dict)
    resetPassword = models.JSONField(default=dict)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    @classmethod
    def is_phone_unique(cls, phone):
        try:
            cls.objects.get(phone=phone)
            return False
        except cls.DoesNotExist:
            return True

    @classmethod
    def is_email_unique(cls, email):
        try:
            cls.objects.get(email=email)
            return False
        except cls.DoesNotExist:
            return True 


class Token(models.Model):
    userId = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="userId")
    token = models.TextField()

    def checkingToken(user, refreshtoken):
        try:
            dbToken = Token.objects.all().get(userId=user.id)
            dbToken.token = refreshtoken
            dbToken.save()
            return None
        except Token.DoesNotExist:
            return True


class AccountIds(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    account = models.ForeignKey(Accounts, on_delete=models.CASCADE)


class CardIds(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE)