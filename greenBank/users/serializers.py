from django.contrib.auth import get_user_model
from rest_framework import serializers
from authentication.models import Users

class PasswordChangeSerializer(serializers.ModelSerializer):
    oldPassword = serializers.CharField(min_length=8, max_length=30)
    newPassword = serializers.CharField(min_length=8, max_length=30)
    confirmNewPassword = serializers.CharField(min_length=8, max_length=30)
    
    class Meta:
        fields = ["oldPassword", "newPassword", "confirmNewPassword"]
        model = Users

class UserGettingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    firstName = serializers.CharField(max_length=30)
    lastName = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(max_length=20, write_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=256)
    img = serializers.FileField()


    class Meta:
        model = Users
        fields = [
            "id",
            "firstName",
            "lastName",
            "email",
            "password",
            "phone",
            "birthday",
            "img",
        ]
        extra_kwargs = {"password": {"write_only": True}}
        

class GettingTransactionHistoryByUserId(serializers.ModelSerializer):
    userId = serializers.IntegerField()
    
    class Meta:
        model = Users
        fields = ["userId"]
        
        
class ChnageUserDataSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(max_length=30, required=False)
    lastName = serializers.CharField(max_length=30, required=False)
    phone = serializers.CharField(max_length=256, required=False)
    img = serializers.FileField(required=False)
    class Meta:
        model = Users
        fields = [
            "firstName",
            "lastName",
            "phone",
            "img",
        ]
        

class SendCurrentEmailSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField()
    email = serializers.EmailField()
    
    class Meta:
        model = Users
        fields = [
            "userId",
            "email",
        ]
        
class VerifyAndWriteNewEmailSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField()
    newEmail = serializers.EmailField()
    number = serializers.CharField(min_length=4, max_length=4)
    
    class Meta:
        model = Users
        fields = [
            "userId",
            "number",
            "newEmail",
        ]