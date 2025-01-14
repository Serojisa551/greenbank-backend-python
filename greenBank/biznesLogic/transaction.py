from rest_framework.response import Response
from accounts.models import Accounts
from cards.models import Cards
from transaction.serializers import *
from transaction.utils import *
from accounts.utils import decoding
from transaction.models import Transactions
from authentication.models import *
from rest_framework import status
from datetime import datetime
import jwt, datetime
from users.utils import getPayload
from django.conf import settings


def gettiingHistory(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    if False == serializedData:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    return serializedData


def get_transaction_history_by_number(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    number = request.GET.get("number")
    userId = request.GET.get("userId")
    length = len(number)
    payload = getPayload(request.COOKIES)
    transactions = []
    if False == serializedData:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    if payload["is_superuser"] == True:
        if length == 16:
            card = Cards.objects.get(cardNumber=number)
            user = CardIds.objects.filter(card=card)
        elif length == 20:
            account = Accounts.objects.get(accountNumber=number)
            user = AccountIds.objects.get(account=account)
        else:
            raise ValueError("length number It should be either 20 or 16")
        for elem in serializedData:
            if int(userId) == user.user.id:
                if elem["sender"] == number or elem["receiver"] == number:
                    transactions.append(elem)
    else:
        is_user_account = False
        is_user_card = False
        if length == 16:
            cards = CardIds.objects.filter(user=userId)
            for card in cards:
                cardNumber = card.card.cardNumber
                if cardNumber == number:
                    is_user_card = True
                    for elem in serializedData:
                        if elem["sender"] == number or elem["receiver"] == number:
                            transactions.append(elem)
        elif length == 20:
            accounts = AccountIds.objects.filter(user=userId)
            for account in accounts:
                accountNumber = account.account.accountNumber
                if accountNumber == number:
                    is_user_account = True
                    for elem in serializedData:
                        if elem["sender"] == number or elem["receiver"] == number:
                            transactions.append(elem)
        else:
            raise ValueError("length number It should be either 20 or 16")
        if not (is_user_account or is_user_card):
            raise ValueError("This account or card does not belong to the user")
    return transactions


def get_transaction_history_by_date(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')
    filtered_transactions = []
    if serializedData == False:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    for transaction in serializedData:
        if start_date_str <= transaction['date'] <= end_date_str:
            filtered_transactions.append(transaction)
    return filtered_transactions


def getTransactionHistoryByAmount(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    miniumAmount = request.GET.get("miniAmount")
    maxumAmount = request.GET.get("maxAmount")
    if serializedData == False:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    if maxumAmount is None:
        data = miniAmount(serializedData, miniumAmount)
    elif miniumAmount is None:
        data = maxAmount(serializedData, maxumAmount)
    elif miniumAmount and maxumAmount:
        data = maxAndMiniAmount(serializedData, miniumAmount, maxumAmount)
    return data


def getTransactionHistoryByDescriptions(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    description = request.GET.get("description")
    filteredTransactions = []
    if serializedData == False:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
        )
    for elem in serializedData:
        elem = dict(elem)
        if elem["description"] == description:
            filteredTransactions.append(elem)
    return filteredTransactions


def getTransactionHistoryByIsDone(request, serializedData=None):
    if not serializedData:
        serializedData = history(request)
    userId = int(request.GET.get("userId"))
    payload = getPayload(request.COOKIES)
    payloadId = int(payload["id"])
    if serializedData == False:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    filteredTransactions = []
    for elem in serializedData:
        if elem["is_successful"] == True:
            filteredTransactions.append(elem)
    return filteredTransactions


def getTransactionHistoryByIsCredit(request):
    userId = int(request.GET.get("userId"))
    serializedData = history(request, True)
    if False == serializedData:
        return Response(
                        {
                        "status": "error",
                        "value": None,
                        "message": "This UserId is not subject to the user"
                        }, status=400
                        )
    filteredTransactions = []
    for elem in serializedData:
        if int(elem["user_id"]) == userId:
            filteredTransactions.append(elem)
    serializer = GettingTransactionHistory(filteredTransactions, many=True)
    return serializer.data


def accountToAccount(request):
    sender = request.data.get("sender")
    receiver = request.data.get("receiver")
    accountSending = Accounts.objects.get(accountNumber=sender)
    acceptingAccount = Accounts.objects.get(accountNumber=receiver)
    transaction = createTransferForAccount(accountSending, acceptingAccount, request)
    serislizer = GettingTransactionHistory(transaction)
    return Response(
        {
        "status": "success",
        "value": serislizer.data,
        "message": "The transfer was completed successfully"
        }, status=201
        )



def cardToCard(request):
    cardNumberSending = request.data.get("sender")
    acceptingCardNumber = request.data.get("receiver")
    cardSending = Cards.objects.get(cardNumber=cardNumberSending)
    acceptingCard = Cards.objects.get(cardNumber=acceptingCardNumber)
    transaction = createTransferForCard(cardSending, acceptingCard, request)
    serislizer = GettingTransactionHistory(transaction)
    return Response(
        {
        "status": "success",
        "value": serislizer.data,
        "message": "The transfer was completed successfully"
        }, status=201
        )


def EasyTransver(request):
    phone = request.data.get("sender")
    accountNumberSending= request.data.get("receiver")
    accountSending = defaultAccountSercher(phone)
    acceptingAccount = Accounts.objects.get(accountNumber=accountSending.accountNumber)
    transaction = createTransferForAccount(accountSending, acceptingAccount, request)
    serislizer = GettingTransactionHistory(transaction)
    return Response(
        {
        "status": "success",
        "value": serislizer.data,
        "message": "The transfer was completed successfully"
        }, status=201
        )


def creatingQRToken(request):
    number = request.GET.get("number")
    payload = {
        "number": number,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        "iat": datetime.datetime.utcnow(),
    }
    length = len(number)
    if length == 16:
        payload["type"] = "QR-card"
    elif length == 20:
        payload["type"] = "QR-account"
    else:
        raise ValueError("length number It should be either 20 or 16")
    
    QRToken = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    return Response(
        {
        "status": "success",
        "value": QRToken,
        "message": "Data successfully encrypted"
        }, status=200)


def TransferToQR(request):
    QRToken = request.data.get("sender")
    payload = decoding(QRToken)
    
    if type(payload) != dict:
        return payload
    
    typeTransfer = payload["type"]
    NumberSending = payload["number"]
    acceptingNumber = request.data.get("receiver")
    if typeTransfer == "QR-account":
        accountSending = Accounts.objects.get(accountNumber=NumberSending)
        acceptingAccount = Accounts.objects.get(accountNumber=acceptingNumber)
        transaction = createTransferForAccount(accountSending, acceptingAccount, request, typeTransfer)
    elif typeTransfer == "QR-card":
        cardSending = Cards.objects.get(cardNumber=NumberSending)
        acceptingCard = Cards.objects.get(cardNumber=acceptingNumber)
        transaction = createTransferForCard(cardSending, acceptingCard, request, payload)
    serislizer = GettingTransactionHistory(transaction)
    return Response(
        {
        "status": "success",
        "value": serislizer.data,
        "message": "The transfer was completed successfully"
        }, status=201
        )
