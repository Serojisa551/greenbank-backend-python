from accounts.utils import generatedAccountNumber
from django.shortcuts import get_object_or_404
from authentication.models import CardIds, Users
from cards.models import Cards
from datetime import datetime, timedelta
from accounts.models import Accounts
from random import randint
from .models import *


def generatedcardNumber(cardType):
    while True:
        if cardType == "visa":
            cardNumber = "4"
        else:
            cardNumber = "5"
        for i in range(15):
            cardNumber += str(randint(0, 9))
        try:
            number = Cards.objects.all().get(cardNumber=cardNumber)
            continue
        except Cards.DoesNotExist:
            return cardNumber


def generatedCVV():
    CVV = ""
    for i in range(3):
        CVV += str(randint(0, 9))
    return CVV


def add_ten_days():
    current_date = datetime.now().date()
    future_date = current_date + timedelta(days=3652)
    return future_date


def createAccountForCard(currency):
    accountNumber = generatedAccountNumber()
    account = Accounts(
        accountType="current",
        currency=currency,
        accountNumber=accountNumber,
    )
    account.save()
    return account


def cardIdSaver(email, cardNumber):
    try:
        user = Users.objects.get(email=email)
        card = Cards.objects.get(cardNumber=cardNumber)
        cardId = CardIds(user=user, card=card)
        cardId.save()
        return card
    except Users.DoesNotExist:
        return {
                "status":"error",
                "value":None,
                "message":f"A user with this email does not exist '{email}'"
                }
    except Cards.DoesNotExist:
        return {
                "status":"error",
                "value":None,
                "message":f"A account with this number does not exist '{accountNumber}'"
                }



def deleteCardById(id):
    try:
        card = Cards.objects.get(id=id)
        if card.is_deleted:
            return {"message": "This account has already been deleted"}
        card.is_deleted = True
        card.save()
    except Cards.DoesNotExist:
        return ({"message": f"A card with this ID does not exist '{id}'"})
