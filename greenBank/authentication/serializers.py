from rest_framework import serializers
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(max_length=30)
    lastName = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(min_length=8, max_length=30, write_only=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=256)

    class Meta:
        model = Users
        fields = [
            "firstName",
            "lastName",
            "email",
            "password",
            "phone",
            "birthday",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["email", "password"]


class CheckActivCodeSerializer(serializers.ModelSerializer):
    number = serializers.CharField(min_length=4, max_length=4)
    userId = serializers.IntegerField()
    class Meta:
        model = Users
        fields = ["number", "userId"]
                
                
class EmailValidationSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField()
    email = serializers.EmailField()
    
    class Meta:
        model = Users
        fields = [
            "userId",
            "email",
        ]
        

class ResetPasswordSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField()
    password = serializers.CharField(min_length=8, max_length=30)
    
    class Meta:
        model = Users
        fields = [
            "userId",
            "password",
        ]
        