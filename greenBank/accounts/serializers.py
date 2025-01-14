from rest_framework import serializers
from .models import *
from .enum import *


class ReadCreateAccountSerializer(serializers.ModelSerializer):
    accountType = serializers.ChoiceField(
        choices=[
            (accountType.value, accountType.name.replace("_", " ").title())
            for accountType in AccountType
        ],
        label="Account Type",
    )
    currency = serializers.ChoiceField(
        choices=[
            (currency.value, currency.name.replace("_", " ").title())
            for currency in CardCurrencyType
        ],
        label="Account Currency",
    )

    class Meta:
        model = Accounts
        fields = ["accountName", "accountType", "currency"]


class WriteCreateAccountSerializer(ReadCreateAccountSerializer, serializers.ModelSerializer):
    userId = serializers.IntegerField()

    class Meta:
        model = Accounts
        fields = ["userId","accountName", "accountType", "currency"]


class AccountGettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ["id", "accountName", "accountNumber", "balance", "currency", "accountType", "isDefault"]



class UpdateAccountNameSerializer(serializers.ModelSerializer):
    accountName = serializers.CharField(required=True)

    class Meta:
        model = Accounts
        fields = ["accountName"]
