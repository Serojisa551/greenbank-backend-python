from django.utils.decorators import decorator_from_middleware_with_args
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from email.mime.multipart import MIMEMultipart
from rest_framework.response import Response
from mongoengine.fields import Decimal128
from rest_framework.views import APIView
from biznesLogic.resetPassword import *
from accounts.models import Accounts
from accounts.utils import decoding
from users.utils import getPayload
from rest_framework import status
from drf_yasg import openapi
from .serializers import *
from .models import Token
from .models import *
from .utils import *
import os


 
@swagger_auto_schema(method="post", request_body=UserRegistrationSerializer)
@api_view(["POST"])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    email = request.data.get("email")
    phone = request.data.get("phone")
    password = make_password(request.data.get("password"))
    if not Users.is_email_unique(email):
        return Response({
                        "status":"error",
                        "value": None,
                        "message":"This email has already been registered"
                    }, status=400
                    )
    if not Users.is_phone_unique(phone):
        return Response({
                        "status":"error",
                        "value": None,
                        "message":"This phone number has already been registered"
                    }, status=400
                    )
       
    code = verificationCode()  
    try:    
        send_email(email, code)
    except Exception as e:
        return Response({
                        "status":"error",
                        "value": None,
                        "message":f"{e}"
                        }, status=500)
    
    if serializer.is_valid():
        serializer.save()
    
    user = Users.objects.get(email=email)
    user.password = password
    user.activationCode = code
    user.expirationActivationCode = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    user.save()
    return Response({
                        "status":"success",
                        "value":{"userId":user.id},
                        "message":"Registered is successfully"
                    }, status=201
                    )


@swagger_auto_schema(method="post", request_body=CheckActivCodeSerializer)
@api_view(["POST"])
def checkActiveCcode(request):
    userId = request.data.get("userId")
    code = request.data.get("number")
    user = Users.objects.get(id=userId)
    current_time = datetime.datetime.now()
    time_str = current_time.strftime('%H:%M:%S')
    expirationActivationCode =user.expirationActivationCode.strftime('%H:%M:%S')
    if expirationActivationCode > time_str:
        if user.activationCode == code:
            user.is_active = True
            user.activationCode = None
            user.expirationActivationCode = None
        else:
            return Response ({
                                "status": "error",
                                "value": None,
                                "message": "Your code does not match the code we sent you"
                            }, status=400)
    else:
        return Response({
                        "status": "error",
                        "value": None,
                        "message": "The activation code time is over"
                    }, status=400)
    accountNumber = createAccountForRergister()
    accountId = accountIdSaver(user.email, accountNumber)
    
    if type(accountId) == dict:
        return Response(accountId)
    
    accessToken = createAccessToken(user)
    refreshToken = createRefreshToken(user)
    
    userDto = getUserAccountsAndCards(user.id)
    
    user.save()
    
    response = Response()
    response.set_cookie(key="refreshToken", value=refreshToken)
    response.data = {
                    "status" : "success",
                    "value" : {
                                "accessToken": accessToken,
                                "userDto": userDto
                              },
                    "message" : "user successfully registered"
                    }
    return response 


@ratelimit(key='ip', rate='1/m')
@api_view(["PATCH"])
def refreshActivationCode(request, userId):
    user =  Users.objects.get(id=userId)
    code = verificationCode()
    try:    
        send_email(user.email, code)
    except Exception:
        return Response({
                        "status":"error",
                        "value":None,
                        "message":"Internal server error"}
                        , status=500)
    
    user.activationCode = code
    user.expirationActivationCode = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    user.save()
    return Response({
                    "status":"success",
                    "value":None,
                    "message": "New activation code is successfully refreshed"
                    }, status=200)


@swagger_auto_schema(method="post", request_body=UsersSerializer)
@api_view(["POST"])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = Users.objects.get(email=email)

    accessToken = createAccessToken(user)
    refreshToken = createRefreshToken(user)
    
    userDto = getUserAccountsAndCards(user.id)

    response = Response()
    response.set_cookie(key="refreshToken", value=refreshToken)
    response.data =  {
                    "status" : "success",
                    "value" : {
                                "accessToken": accessToken,
                                "userDto": userDto
                              },
                    "message" : "user successfully login"
                    }
    return response


@api_view(["DELETE"])
def logout_user(request):
    token = request.COOKIES.get("refreshToken")
    if not token:
        return Response(
            {
            "status":"error",
            "value":None,
            "message":"Unauthenticated!"
            }, status=400)

    payload = decoding(token)
    if type(payload) != dict:
        return payload
    userId = payload.get("id")

    refreshToken = Token.objects.get(userId_id=userId)
    refreshToken.delete()

    response = Response()
    response.delete_cookie("refreshToken")
    response.data = {
                    "status":"success",
                    "value":{},
                    "message":"user successfully logged out"
                    }
    return response


@api_view(["GET"])
def refresh(request):
    token = request.COOKIES.get("refreshToken")
    if not token:
        return Response(
            {
            "status": "error",
            "value": None,
            "message": "Unauthenticated!"
            }, status=400)
    payload = decoding(token)
    try:
        refreshToken = Token.objects.get(token=token)
        user_id = refreshToken.userId_id
        user = Users.objects.get(id=user_id)
        accessToken = createAccessToken(user)
    except Token.MultipleObjectsReturned:
        return Response(
            {
            "status": "error",
            "value": None,
            "message": "Multiple tokens found"
            }, status=400)
    except ObjectDoesNotExist:
        return Response(
            {
            "status": "error",
            "value": None,
            "message":"Token not found"
            }, stats=400)
    return Response({
                    "status": "success",
                    "value": {
                                "accessToken": accessToken
                             },
                    "message": "access token refreshed"
                    }, status=200)


@swagger_auto_schema(
    method="POST",
    request_body=CheckActivCodeSerializer
)
@swagger_auto_schema(
    method="PATCH",
    request_body=EmailValidationSerializer
)
@api_view(["PATCH", "POST"])
def forgetPassword(request):
    data = ""
    if request.method == "PATCH":
       data = resetPasswordSendEmail(request)
    elif request.method == "POST":
        data = resetPasswordVerifyEmail(request)
    return data


@swagger_auto_schema(
    method="PATCH",
    request_body=ResetPasswordSerializer
)
@api_view(["PATCH"])
def resetPassword(request):
    return changePassword(request)