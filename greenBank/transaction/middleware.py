from authentication.models import AccountIds, CardIds
from django.shortcuts import get_object_or_404
from mongoengine.fields import Decimal128
from accounts.models import Accounts
from django.http import JsonResponse
from authentication.models import *
from cards.models import Cards
from .utils import getPayload
from accounts.utils import *
from .utils import *
import json


class TransactionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            if request.path.startswith("/api/transaction/createQRToken"):
                data = json.loads(request.body.decode("utf-8"))
                number = data.get("number")
                payload = getPayload(request.COOKIES)
                userId = payload["id"]
                self.verificationCreateQR(
                    number,
                    userId,
                )
            if request.path.startswith("/api/transaction/"):
                data = json.loads(request.body.decode("utf-8"))
                typeTransfer = data.get("type").lower()
                typeTransfer = typeTransfer
                if typeTransfer == "account":
                    acceptingAccountNumber = data.get("receiver")
                    accountNumberSending = data.get("sender")
                    amount = data.get("amount")
                    currency = data.get("currency")
                    purpose = data.get("purpose")
                    self.checkAmount(amount)
                    payload = getPayload(request.COOKIES)
                    userId = payload["id"]
                    self.verificationАccount(
                        accountNumberSending,
                        acceptingAccountNumber,
                        userId,
                        amount,
                        currency,
                        purpose,
                    )
                if typeTransfer == "card":
                    sender = data.get("sender")
                    acceptingCardNumber = data.get("receiver")
                    amount = data.get("amount")
                    currency = data.get("currency")
                    purpose = data.get("purpose")
                    self.checkAmount(amount)
                    payload = getPayload(request.COOKIES)
                    userId = payload["id"]
                    self.verificationCard(
                        sender,
                        acceptingCardNumber,
                        userId,
                        amount,
                        currency,
                        purpose,
                    )
                if typeTransfer == "phone":
                    acceptingAccountNumber = data.get("receiver")
                    phone = data.get("sender")
                    amount = data.get("amount")
                    currency = data.get("currency")
                    purpose = data.get("purpose")
                    self.checkAmount(amount)
                    payload = getPayload(request.COOKIES)
                    userId = payload["id"]
                    self.verificationEasyTransver(
                        acceptingAccountNumber,
                        phone,
                        userId,
                        amount,
                        currency,
                        purpose,
                    )
                if typeTransfer  == "qr_account" or typeTransfer  == "qr_card":
                    NumberReceiver = data.get("receiver")
                    QRToken = data.get("sender")
                    amount = data.get("amount")
                    currency = data.get("currency")
                    purpose = data.get("purpose")
                    payload = getPayload(request.COOKIES)
                    QRToken = decoding(QRToken)
                    self.checkAmount(amount)
                    if type(payload) != dict:
                        return payload
                    userId = payload["id"]
                    self.verificationTrensferForQR(userId, NumberReceiver,amount, currency, purpose, QRToken)
        except json.JSONDecodeError:
            pass
        except ValueError as e:
            return JsonResponse({
                            "status":"error",
                            "value": None,
                            "message": f"{e}"
                            }, status=400)
        response = self.get_response(request)
        return response
    

    def verificationTrensferForQR(self, userId, NumberReceiver, amount, currency, purpose, QRToken):
        try:
            if type(QRToken) != dict:
                raise ValueError("Invalid token")
            typeTransfer  = QRToken["type"]
            accountSendingNumber = QRToken["number"]
            if typeTransfer  == "QR-account":
                accountSending = Accounts.objects.all().get(
                    accountNumber=accountSendingNumber
                )
                acceptingAccount = Accounts.objects.all().get(
                    accountNumber=NumberReceiver
                )
                self.account_is_deleted(accountSending, acceptingAccount)
                self.checkSenderReseiver(QRToken["number"], NumberReceiver)
                accountId = AccountIds.objects.all().get(account_id=accountSending.id)
                if (
                    accountSending.currency != currency
                    and acceptingAccount.currency != currency
                ):
                    saveTransaction(
                        userId,
                        accountSendingNumber,
                        NumberReceiver,
                        amount,
                        purpose,
                        typeTransfer ,
                        False,
                    )
                    raise ValueError("The currency must match the currency of the account")
                if self.is_account_owner(userId, accountId):
                    raise ValueError("This account does not belong to the user")
                if int(float(str(accountSending.balance))) < amount:
                    saveTransaction(
                        userId,
                        accountSendingNumber,
                        NumberReceiver,
                        amount,
                        purpose,
                        typeTransfer ,
                        False,
                    )
                    raise ValueError("Insufficient funds")
            elif typeTransfer == "QR-card":
                cardSending = Cards.objects.all().get(cardNumber=accountSendingNumber)
                acceptingCard = Cards.objects.all().get(cardNumber=NumberReceiver)
                self.card_is_deleted(cardSending, acceptingCard)
                self.checkSenderReseiver(QRToken["number"], NumberReceiver)
                cardId = CardIds.objects.all().get(card=cardSending)
                if (
                    cardSending.cardCurrency != currency
                    and acceptingCard.cardCurrency != currency
                ):
                    saveTransaction(
                        userId,
                        accountSendingNumber,
                        NumberReceiver,
                        amount,
                        purpose,
                        typeTransfer ,
                        False,
                    )
                    raise ValueError("The currency must match the currency of the card")
                if cardId.user.id != int(userId):
                    raise ValueError("This card does not belong to the user")
                if int(float(str(cardSending.account.balance))) < amount:
                    saveTransaction(
                        userId,
                        accountSendingNumber,
                        NumberReceiver,
                        amount,
                        purpose,
                        typeTransfer ,
                        False,
                    )
                    raise ValueError("Insufficient funds")
        except Cards.DoesNotExist:
            raise ValueError("Such an card does not exist")
        except CardIds.DoesNotExist:
            pass
        except Accounts.DoesNotExist:
            raise ValueError("Such an account does not exist")
        except AccountIds.DoesNotExist:
            raise ValueError("this account is designed for card")
    
    def verificationCard(
        self,
        cardNumberSending,
        acceptingCardNumber,
        userId,
        amount,
        currency,
        purpose,
    ):
        try:
            cardSending = Cards.objects.all().get(cardNumber=cardNumberSending)
            acceptingCard = Cards.objects.all().get(cardNumber=acceptingCardNumber)
            self.card_is_deleted(cardSending, acceptingCard)
            self.checkSenderReseiver(cardNumberSending, acceptingCardNumber)
            cardId = CardIds.objects.all().get(card=cardSending)
            if (
                cardSending.cardCurrency != currency
                and acceptingCard.cardCurrency != currency
            ):
                saveTransaction(
                    userId,
                    cardNumberSending,
                    acceptingCardNumber,
                    amount,
                    purpose,
                    "card",
                    False,
                )
                raise ValueError("The currency must match the currency of the card")
            if cardId.user.id != int(userId):
                raise ValueError("This card does not belong to the user")
            if int(float(str(cardSending.account.balance))) < amount:
                saveTransaction(
                    userId,
                    cardNumberSending,
                    acceptingCardNumber,
                    amount,
                    purpose,
                    "card",
                    False,
                )
                raise ValueError("Insufficient funds")
        except Cards.DoesNotExist:
            raise ValueError("Such an card does not exist")
        except CardIds.DoesNotExist:
            pass

    def verificationАccount(
        self,
        accountNumberSending,
        acceptingAccountNumber,
        userId,
        amount,
        currency,
        purpose,
    ):
        try:
            acceptingAccount = Accounts.objects.all().get(
                accountNumber=acceptingAccountNumber
            )
            accountSending = Accounts.objects.all().get(
                accountNumber=accountNumberSending
            )
            self.account_is_deleted(accountSending, acceptingAccount)
            self.checkSenderReseiver(accountNumberSending, acceptingAccountNumber)
            accountId = AccountIds.objects.all().get(account_id=accountSending.id)
            if (
                accountSending.currency != currency
                and acceptingAccount.currency != currency
            ):
                saveTransaction(
                    userId,
                    accountNumberSending,
                    acceptingAccountNumber,
                    amount,
                    purpose,
                    "account",
                    False,
                )
                raise ValueError("The currency must match the currency of the account")
            if self.is_account_owner(userId, accountId):
                raise ValueError("This account does not belong to the user")
            if int(float(str(accountSending.balance))) < amount:
                saveTransaction(
                    userId,
                    accountNumberSending,
                    acceptingAccountNumber,
                    amount,
                    purpose,
                    "account",
                    False,
                )
                raise ValueError("Insufficient funds")
        except Accounts.DoesNotExist:
            raise ValueError("Such an account does not exist")
        except AccountIds.DoesNotExist:
            raise ValueError("this account is designed for card")
        
    def verificationEasyTransver(
        self,
        acceptingAccountNumber,
        phone,
        userId,
        amount,
        currency,
        purpose,
    ):
        try:
            user = Users.objects.get(phone=phone)
            accountSending = defaultAccountSercher(phone)
            acceptingAccount = Accounts.objects.all().get(
                accountNumber=acceptingAccountNumber
            )
            self.account_is_deleted(accountSending, acceptingAccount)
            self.checkSenderReseiver(accountSending.accountNumber, acceptingAccountNumber)
            accountId = AccountIds.objects.all().get(account=accountSending)
            if (
                accountSending.currency != currency
                and acceptingAccount.currency != currency
            ):
                saveTransaction(
                    userId,
                    accountNumberSending,
                    acceptingAccount.accountNumber,
                    amount,
                    purpose,
                    "phone",
                    False,
                )
                raise ValueError("The currency must match the currency of the account")
            if self.is_account_owner(userId, accountId):
                raise ValueError("This account does not belong to the user")
            if int(float(str(accountSending.balance))) < amount:
                saveTransaction(
                    userId,
                    accountNumberSending,
                    acceptingAccount.accountNumber,
                    amount,
                    purpose,
                    "phone",
                    False,
                )
                raise ValueError("Insufficient funds")
        except Users.DoesNotExist:
            raise ValueError("Such an user does not exist")
        except Accounts.DoesNotExist:
            raise ValueError("Such an account does not exist")
        except AccountIds.DoesNotExist:
            raise ValueError("this account is designed for card")


    def checkAmount(self, amount):
        if amount < 0 or amount > 99999999:
            raise ValueError(f"The sum must be a positive number from 0 to 999,999,99 and not '{amount}'.")
        
    def is_account_owner(self, userId, account):
        if account.user.id != int(userId):
            return True
        return False
    
    
    def verificationCreateQR(
        self,
        number,
        userId,
    ):
        try:
            accountSending = Accounts.objects.all().get(
                accountNumber=number
            )
            accountId = AccountIds.objects.all().get(account=accountSending)
            if self.is_account_owner(userId, accountId):
                raise ValueError("This account does not belong to the user")
        except Accounts.DoesNotExist:
            raise ValueError("Such an account does not exist")
        except AccountIds.DoesNotExist:
            raise ValueError("this account is designed for card")
    
    def account_is_deleted(self, accountSending, acceptingAccount):
        if accountSending.is_deleted:
            raise ValueError(f"This account is deleted '{accountSending.accountNumber}'")
        if acceptingAccount.is_deleted:
            raise ValueError(f"This account is deleted '{acceptingAccount.accountNumber}'")
        
    def card_is_deleted(self, cardSending, acceptingCard):
        if cardSending.is_deleted:
            raise ValueError(f"This a card is deleted '{cardSending.cardNumber}'")
        if acceptingCard.is_deleted:
            raise ValueError(f"This a cardis deleted '{acceptingCard.cardNumber}'") 
        
    def checkSenderReseiver(self, sender, reseiver):
        if sender == reseiver:
            raise ValueError("Sender and reseiver they can't match")