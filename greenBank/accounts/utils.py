from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from mongoengine.fields import Decimal128
from authentication.models import Users
from django.conf import settings
from rest_framework.response import Response
from random import randint
from .models import *
import jwt, datetime


def generatedAccountNumber():
    while True:
        accountNumber = ""
        for i in range(20):
            accountNumber += str(randint(0, 9))
        try:
            number = Accounts.objects.all().get(accountNumber=accountNumber)
            continue
        except Accounts.DoesNotExist:
            return accountNumber


def decoding(headers):
    try:
        print(headers, "hello")
        if not headers:
            raise ValueError(f"Тhe parameter for decoding can not be '{headers}'")
        if not (str == type(headers)):
            headers = headers["Authorization"]
        if headers[:6] == "Bearer":
            headers = headers.split(" ")[1]
        payload = jwt.decode(headers, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except TypeError:
        return Response(
            {
            "status": "error",
            "value": None,
            "message":"Token has expired"
            })
    except jwt.InvalidTokenError:
        return Response(
            {
            "status": "error",
            "value": None,
            "message":"Invalid token"
            }, status=400)


def deleteAccountById(id):
    try:
        account = Accounts.objects.get(id=id)
        account.balance = Decimal128.to_decimal(account.balance)
        account.is_deleted = True
        account.save()
    except Accounts.DoesNotExist:
        raise ValueError(f"A account with this ID does not exist '{id}'")
