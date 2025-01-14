from django.shortcuts import get_object_or_404
from transaction.models import Transactions
from authentication.models import Users, AccountIds
from accounts.models import *
from datetime import datetime
from rest_framework.response import Response
from accounts.models import Accounts
from cards.models import Cards
from .serializers import *
from .models import Transactions
from authentication.models import *
from users.utils import getPayload
import os
import decimal

def saveTransaction(userId, sender, receiver, amount, description, type, is_successful):
    user = Users.objects.get(id=userId)
    deta = datetime.now().date()
    rounded_amount = decimal.Decimal(amount).quantize(decimal.Decimal('0.01'))
    transaction = Transactions(
        user=user,
        sender=sender,
        receiver=receiver,
        amount=amount,
        description=description,
        type=type,
        date=deta,
        is_successful=is_successful,
    )
    transaction.save()
    return transaction

def history(request, typeHistory=None):
    userId = int(request.GET.get("userId"))
    payload = getPayload(request.COOKIES)
    payloadId = payload["id"]
    if not payload["is_superuser"]:
        if payloadId != userId:
            return False
    page = int(request.GET.get("page"))
    user = get_object_or_404(Users, id=userId)

    history_transactions = Transactions.objects.filter(user=user)

    card_ids = CardIds.objects.filter(user=user)
    account_ids = AccountIds.objects.filter(user=user)

    accounts = [
        get_object_or_404(Accounts, id=acc_id.account.id) for acc_id in account_ids
    ]
    cards = [get_object_or_404(Cards, id=card_id.card.id) for card_id in card_ids]
    
    serializer = GettingTransactionHistoryForCredit(history_transactions, many=True)
    serializedData = serializer.data
    for card in cards:
        transactions_for_card = Transactions.objects.filter(receiver=card.cardNumber)
        for transaction_for_card in transactions_for_card:
            if transaction_for_card.is_successful:
                serialized_transaction = GettingTransactionHistoryForCredit(
                    transaction_for_card
                ).data
                serializedData.append(serialized_transaction)
                
    for account in accounts:
        transactions_for_account = Transactions.objects.filter(
            receiver=account.accountNumber
        )
        for transaction_for_account in transactions_for_account:
            if transaction_for_account.is_successful:
                serialized_transaction = GettingTransactionHistoryForCredit(
                    transaction_for_account
                ).data
                serializedData.append(serialized_transaction)
    if not typeHistory:
        serializer = GettingTransactionHistory(serializedData, many=True)
        serializedData = serializer.data
    size = request.GET.get("size")
    serializedData = slicer(page, size, serializedData)
    return serializedData


def slicer(page, size, data):
    if page == 1:
        pageElementsStart = 0
        pageElementsStop = int(size)
    else:
        pageElementsStart = int(page - 1) * int(size)
        pageElementsStop = pageElementsStart  + int(size)
    length = len(data)
    if length > pageElementsStart and length > pageElementsStop:
        return data[pageElementsStart:pageElementsStop]
    elif (length > pageElementsStart and length == pageElementsStop) or page == 1:
        return data[pageElementsStart:]
    else:
        return []
    

def miniAmount(serializedData, miniAmount):
    transactions = []
    miniAmount = int(miniAmount)
    for elem in serializedData:
        if int(float(elem["amount"])) > miniAmount:
            transactions.append(elem)
    return transactions


def maxAmount(serializedData, maxAmount):
    transactions = []
    maxAmount = int(maxAmount)
    for elem in serializedData:
        if int(float(elem["amount"])) < maxAmount:
            transactions.append(elem)
    return transactions
    
def maxAndMiniAmount(serializedData, miniAmount, maxAmount):
    transactions = []
    miniAmount = int(miniAmount)
    maxAmount = int(maxAmount)
    for elem in serializedData:
        amount = int(float(elem["amount"]))
        if amount > miniAmount and amount < maxAmount:
            transactions.append(elem)
    return transactions

def defaultAccountSercher(phone):
    user = Users.objects.all().get(phone=phone)
    if not user:
        raise ValueError("Therefore, the phone number does not have a registered user.")
    accountIds = AccountIds.objects.filter(user=user)
    for elem in accountIds:
        if elem.account.isDefault == True:
            return elem.account
    else:
        raise ValueError("Default user account not found.")
    

def createTransferForAccount(accountSending, acceptingAccount, request, typeTransfer=None):
    payload = getPayload(request.COOKIES)
    userId = payload["id"]
    amount = request.data.get("amount")
    purpose = request.data.get("purpose")
    if typeTransfer == None:
        typeTransfer = request.data.get("type")
    accountSending.balance = int(float(str(accountSending.balance))) - int(amount)
    acceptingAccount.balance = int(float(str(acceptingAccount.balance))) + int(amount)
    accountSending.save()
    acceptingAccount.save()
    transaction = saveTransaction(
        userId,
        accountSending.accountNumber,
        acceptingAccount.accountNumber,
        amount,
        purpose,
        typeTransfer,
        True,
    )
    return transaction


def createTransferForCard(cardSending, acceptingCard, request, payloadQR=None):
    payload = getPayload(request.COOKIES)
    userId = payload["id"]
    payload = getPayload(request.COOKIES)
    amount = request.data.get("amount")
    purpose = request.data.get("purpose")
    if payloadQR == None:
        typeTransfer = "card"
    else:
        typeTransfer = payloadQR["type"]
    cardSending.account.balance = int(float(str(cardSending.account.balance))) - int(
        amount
    )
    acceptingCard.account.balance = int(
        float(str(acceptingCard.account.balance))
    ) + int(amount)
    cardSending.account.save()
    acceptingCard.account.save()
    transaction = saveTransaction(
                    userId,
                    cardSending.cardNumber,
                    acceptingCard.cardNumber,
                    amount,
                    purpose,
                    typeTransfer,
                    True
                )
    return transaction

def processRequest(request):
    data = request.GET
    validFields = {
        "startDate": "startDate",
        "endDate": "endDate",
        "userId": "userId",
        "number": "number",
        "miniAmount": "miniAmount",
        "maxAmount": "maxAmount",
        "isCredit": "isCredit",
        "isDone": "isDone",
        "description": "description"
    }

    validInputs = set(validFields.keys())
    userInputs = set(data.keys())

    commonInputs = validInputs.intersection(userInputs)

    validatedData = [validFields[field] for field in commonInputs]
    return validatedData

def checkPage(request):
    if int(request.GET.get("page")) <= 0:
            return Response(
                {
                    "status": "error",
                    "value": None,
                    "mesagge": "Page must be a positive integer"
                }
            )