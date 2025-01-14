from django.contrib.auth.hashers import make_password
from authentication.utils import accountIdSaver
from rest_framework.response import Response
from users.utils import getPayload
from rest_framework import status
from cards.serializers import *
from cards.utils import *


def createCard(request):
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
    serializer = ReadCreateCardSerializer(data=request.data)
    cardNumber = generatedcardNumber(request.data["cardType"])
    CVV = make_password(generatedCVV())
    cardExpirationDate = add_ten_days()
    account = createAccountForCard(request.data["cardCurrency"])
    if serializer.is_valid():
        serializer.save(
            cardNumber=cardNumber,
            CVV=CVV,
            cardExpirationDate=cardExpirationDate,
            account=account,
        )
        
        cardId = cardIdSaver(email=email, cardNumber=cardNumber)
        
        if type(cardId) == dict:
            return Response(cardId)
        serializer = CardGettingSerializer(cardId)
        return Response( 
            {
            "status": "success",
            "value": serializer.data,
            "message" : "Card is created"
            }, status=201)
    return Response({
        "status": "error",
        "value": None,
        "message":"Failed validation"
        }, status=400)


def getUserCards(request):
    print(11)
    payload = getPayload(request.COOKIES)
    cards = CardIds.objects.filter(user=payload["id"])
    lst = []
    for card in cards:
        if card.card.is_deleted == False:
            serializer = CardGettingSerializer(card.card)
            lst.append(serializer.data)
        else:
            return Response({
            "status": "error",
            "value": None,
            "message": "Such card does not exist"
            }, status=400)
    return Response({
        "status": "success",
        "value":lst,
        "message": "All user cards are returned"
        }, status=200)


def getCardById(request, cardId):
    try:
        card = Cards.objects.get(id=cardId)
        if card.is_deleted == False:
            serializer = CardGettingSerializer(card)
            return Response({
            "status": "success",
            "value": serializer.data,
            "message": "Card is returned"
            }, status=200)
        else:
            return Response({
            "status": "error",
            "value": None,
            "message": "Such card does not exist"
            }, status=400)
    except Cards.DoesNotExist: 
        return Response({
            "status": "error",
            "value": None,
            "message": "Such card does not exist"
            }, status=400)


def updateCardName(request, cardId):
    payload = getPayload(request.COOKIES)
    cardName = request.data.get("cardName")
    try:
        card = Cards.objects.get(id=cardId)
    except Cards.DoesNotExist: 
        return Response({
            "status": "error",
            "value": None,
            "message": "Such card does not exist"
            }, status=400)
    is_valid = False
    if payload["is_superuser"]:
        card.cardName = cardName
        card.save()
        is_valid = True
    cards = CardIds.objects.filter(user=payload["id"])
    for card in cards:
        id = int(card.card.id)
        if id == cardId:
            card.card.cardName = cardName
            card.save()
            is_valid = True
            card = card.card
            break
        else:
            return Response(
                {
                "status":"error",
                "value": None,
                "message": "This card either does not exist or is not subject to the user"
                },
                status=400,
            )
    if is_valid:
        serializer = CardGettingSerializer(card)
        return Response(
                {
                    "status": "success",
                    "value": serializer.data,
                    "message": "Card name has been successfully changed"
                },
                status=200
            )

def deleteCard(request, cardId):
    payload = getPayload(request.COOKIES)
    is_valid = False
    if payload["is_superuser"] == True:
        cardDeleted = deleteCardById(cardId)
        if cardDeleted:
            return Response(
            {        
            "status":"error",
            "value": None,
            "message": cardDeleted},
            status=400,
        )
        is_valid = True
    else:
        cards = CardIds.objects.filter(user=payload["id"])
        for card in cards:
            id = int(card.card.id)
            if id == cardId:
                deleteCardById(cardId)
                is_valid = True
        else:
            return Response(
                {
                    "status":"error",
                    "value": None,
                    "message": "This card either does not exist or is not subject to the user"
                },
                status=400,
            )
    if is_valid:
        return Response(
            {
            "status": "success",
            "value": {},
            "message": "Card successfully deleted"
            },status=200
        )