from rest_framework import serializers
from accounts.models import Accounts
from accounts.enum import CardCurrencyType, TransverType, QRType
from .models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(required=True)
    receiver = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    purpose = serializers.CharField(max_length=256, required=True)
    currency = serializers.ChoiceField(
        choices=[
            (currency.value, currency.name.replace("_", " ").title())
            for currency in CardCurrencyType
        ],
        label="currency", required=True
    )
    type = serializers.ChoiceField(
        choices=[
            (type.value, type.name.replace("_", " ").title())
            for type in TransverType
        ],
        label="TransverType", required=True
    )
    class Meta:
        model = Accounts
        fields = ["sender", "receiver", "amount", "purpose", "currency", "type"]      
        
class CreateQRSerializer(serializers.ModelSerializer):
    number = serializers.CharField(min_length=16, max_length=20)
    type =  serializers.ChoiceField(
        choices=[
            (type.value, type.name.replace("_", " ").title())
            for type in QRType
        ],
        label="QRType",
    )

    class Meta:
        model = Accounts
        fields = ["number", "type"]
        
        
class GettingTransactionHistory(serializers.Serializer):
    sender = serializers.CharField()
    receiver = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    type = serializers.CharField()
    date = serializers.DateField()
    is_successful = serializers.BooleanField()

    class Meta:
        fields = ['sender', 'receiver', 'amount', 'description', 'type', 'date', 'is_successful']


class GettingTransactionHistoryForCredit(serializers.Serializer):
    user_id = serializers.IntegerField()
    sender = serializers.CharField()
    receiver = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
    type = serializers.CharField()
    date = serializers.DateField()
    is_successful = serializers.BooleanField()

    class Meta:
        fields = ["user_id", 'sender', 'receiver', 'amount', 'description', 'type', 'date', 'is_successful']
               

class InputTransactionHistory(serializers.ModelSerializer):
    startDate = serializers.DateField(required=False)
    endDate = serializers.DateField(required=False)
    number = serializers.CharField(min_length=16, max_length=20, required=False)
    userId = serializers.IntegerField()
    miniAmount = serializers.IntegerField(required=False)
    maxAmount = serializers.IntegerField(required=False)
    isCredit = serializers.BooleanField(required=False)
    isDone = serializers.BooleanField(required=False)
    description = serializers.CharField(required=False)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    
    class Meta:
        model = Transactions
        fields = ["startDate", "endDate", "number", "userId", "miniAmount", "maxAmount", "isCredit", "isDone", "description", "page", "size"]