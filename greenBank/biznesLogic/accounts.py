from django.contrib.auth.hashers import make_password
from authentication.utils import accountIdSaver
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from mongoengine.fields import Decimal128
from authentication.models import *
from accounts.serializers import *
from users.utils import getPayload
from rest_framework import status
from accounts.models import *
from accounts.utils import *


def createAccount(request):
    payload = getPayload(request.COOKIES)
    userId = request.data.get("userId")
    if payload["is_superuser"]:
        user = Users.objects.get(id=userId)
        email = user.email
    else:
        if payload["id"] == userId:
            email = payload["email"]
        else:
            return Response(
                {
                "status":"error",
                "value":None,
                "message": "User can access to data connected to him"
                }, status=403)
    accountNumber = generatedAccountNumber()
    serializer = ReadCreateAccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(accountNumber=accountNumber, isDefault=False)
        account = accountIdSaver(accountNumber=accountNumber, email=email)
        if type(account) == dict:
            return Response(account)
        serializer = AccountGettingSerializer(account)
        return Response( 
            {
            "status": "success",
            "value": serializer.data,
            "message" : "Account is created"
            }, status=201)
    return Response(
        {
        "status":"error",
        "value": None,
        "message":"Failed validation"
        }, status=400)


def getUserAccounts(request):
    payload = getPayload(request.COOKIES)
    accounts = AccountIds.objects.filter(user=payload["id"])
    lst = []
    for account in accounts:
        if account.account.is_deleted == False:
            serializer = AccountGettingSerializer(account.account)
            lst.append(serializer.data)
    return Response(
        {
        "status": "success",
        "value": lst,
        "message" : "All user accounts are returned"
        }, status=200)


def getAccountById(request, accountId):
    account = Accounts.objects.get(id=accountId)
    serializer = AccountGettingSerializer(account)
    return Response( 
        {
        "status": "success",
        "value": serializer.data,
        "message" : "account is returned"
        }, status=200)


def updateAccountName(request, accountId):
    accountName = request.data.get("accountName")
    account = get_object_or_404(Accounts, id=accountId)
    account.accountName = accountName
    account.balance = Decimal128.to_decimal(account.balance)
    account.save()
    serializer = AccountGettingSerializer(account)
    return Response(
        {
        "status": "success",
        "value": serializer.data,
        "message" : "account is returned"
        }, status=200,
    )


def deleteAccount(request, accountId):
    payload = getPayload(request.COOKIES)
    is_valid = False
    if payload["is_superuser"] == True:
        is_valid = True
    else:
        accounts = AccountIds.objects.filter(user=request.user.id)
        for account in accounts:
            if account.account.id == accountId and account.account.is_deleted:
                is_valid = True
                break
        else:
            return Response(
                {
                "status": "error",
                "value": None,
                "message": "This account either does not exist or is not subject to the user"
                }, status=400
                )
    if is_valid:
        deleteAccountById(accountId)
        return Response(
            {
            "status": "success",
            "value": {},
            "message": "Account successfully deleted"
            }, status=200
        )
    else:
        return Response(
            {
            "status": "error",
            "value": None,
            "message": "Such account  does not exist"
            }, status=400
        )