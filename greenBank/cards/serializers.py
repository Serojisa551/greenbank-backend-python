from rest_framework import serializers
from accounts.enum import *
from .models import *


class ReadCreateCardSerializer(serializers.ModelSerializer):
    cardType = serializers.ChoiceField(
        choices=[
            (cardType.value, cardType.name.replace("_", " ").title())
            for cardType in CardType
        ],
        label="Account Type",
    )
    cardCurrency = serializers.ChoiceField(
        choices=[
            (cardCurrency.value, cardCurrency.name.replace("_", " ").title())
            for cardCurrency in CardCurrencyType
        ],
        label="Account Currency",
    )

    class Meta:
        model = Cards
        fields = ["cardName", "cardType", "cardCurrency"]
        extra_kwargs = {"CVV": {"write_only": True}}

class WriteCreateCardSerializer(ReadCreateCardSerializer, serializers.ModelSerializer):
    userId = serializers.IntegerField()

    class Meta:
        model = Cards
        fields = ["userId", "cardName", "cardType", "cardCurrency"]

class CardGettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = [
            "id",
            "cardName",
            "cardNumber",
            "cardType",
            "cardCurrency",
            "cardExpirationDate",
        ]


class UpdateCardNameSerializer(serializers.ModelSerializer):
    cardName = serializers.CharField(required=True)

    class Meta:
        model = Cards
        fields = ["cardName"]
