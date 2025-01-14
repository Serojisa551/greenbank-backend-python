from authentication.serializers import EmailValidationSerializer
from authentication.utils import verificationCode, send_email
from authentication.models import Users, AccountIds, CardIds
from authentication.utils import getUserAccountsAndCards
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from users.serializers import *
from users.utils import *
from cards.utils import *
import datetime
import base64


def get_user(request, userId):
    payload = getPayload(request.COOKIES)
    is_valid = False
    if payload["is_superuser"] == True:
        is_valid = True
    else:
        if (payload["id"] == userId) or is_valid:
            is_valid = True
        else:
            return Response(
                {
                "status":"error",
                "value":None,
                "message": "User can access to data connected to him"
                },status=400)
    if is_valid:
        userDto = getUserAccountsAndCards(userId)
        return Response(
            {
            "status": "success",
            "value":userDto,
            "message": "User successfully deleted"
            },status=200)


def deleteUser(request, userId):
    payload = getPayload(request.COOKIES)
    is_valid = False
    if payload["is_superuser"] == True:
        is_valid = True
    else:
        if payload["id"] == userId:
            is_valid = True
        else:
            return Response(
                {
                "status":"error",
                "value":None,
                "message": "User can access to data connected to him"
                }, status=403)
    if is_valid:
        try:
            deleteUserById(userId)
            response = Response(status=200)
            response.delete_cookie("refreshToken")
            response.data = {
                "status": "success",
                "value":{},
                "message": "User successfully deleted"
                }
            return response
        except ValueError as e:
            return Response(
                {
                "status": "error",
                "value":None,
                "message": f"{e}"
                },status=400)
                
      
def changeUserData(request, userId):
    payload = getPayload(request.COOKIES)
    filter_data = filterData(request.data)
    is_valid = False
    if type(filter_data) != dict:
        return filter_data
    if payload["is_superuser"] == True:
        is_valid = True
    else:
        if payload["id"] == userId:
            is_valid = True
        else:
            return Response(
                {
                "status":"error",
                "value":None,
                "message": "User can access to data connected to him"
                },status=403)
    if is_valid == True:
        changingUserData(request, userId)
        userDto = getUserAccountsAndCards(userId)
        return Response(
                {
                "status": "success",
                "value": userDto,
                "message": "User data successfully changing"
                }, status=200)
            
        
def gettingAllUsers(request):
    payload = getPayload(request.COOKIES)
    if payload["is_superuser"] == True:
        users = Users.objects.all()
        ls = []
        for user in users:
            if not user.is_deleted:
                ls.append(getUserAccountsAndCards(user.id))
        return Response(
                        {
                        "status": "success",
                        "value": ls,
                        "message": "User data successfully changing"
                        }, status=200)
    else:
        return Response(
                {
                    "status": "error",
                    "value": None,
                    "message": "User cannot access this endpoint"
                },status=403)


def gettingUserImg(request, imgId):
    user = Users.objects.get(id=imgId)
    image_data = user.img.read()
    image_data_base64 = base64.b64encode(image_data).decode('utf-8')
    return Response(
        {
            "status": "success",
            "value": {
                "id": user.id,
                "type": "image/png",
                "imageData": image_data_base64
            },
            "message": "Image successfully returned"
        }
    )
# def gettingUserImg(request, imgId):
#     user = Users.objects.get(id=imgId)
#     image_data = user.img.read()  # Read binary data

#     # Set the content type to image/png
#     response = HttpResponse(image_data, content_type='image/png')

#     # Optionally set the Content-Disposition header to suggest a filename
#     response['Content-Disposition'] = f'attachment; filename="{user.img.name}"'

#     return response


def changingPassword(request):
    payload = getPayload(request.COOKIES)
    user = Users.objects.get(id=payload["id"])
    user.password = make_password(request.data.get("newPassword"))
    user.save()
    return Response({
                    "status":"success",
                    "value":{},
                    "message": "Change password is successfully"
                    }, status=200)


def sendingCurrentEmail(request):
    email = request.data.get("email")
    user = Users.objects.get(email=email)
    code = verificationCode()
    user.email_details =  {
        "oldEmail": email,
        "oldEmailCode": code,
        "oldEmailCodeExpires": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "canChangeEmail": True
    }
    user.save()
    send_email(email, code)
    return Response(
        {
        "status":"success",
        "value":{"userId":user.id},
        "message":"Email confirmation sent successfully"
        }, status=200
        )


def verifyAndWriteNewEmail(request):
    userId = request.data.get("userId")
    oldcode = request.data.get("number")
    newEmail = request.data.get("newEmail")
    user = Users.objects.get(id=userId)
    email_details = user.email_details
    current_time = datetime.datetime.now()
    time_str = current_time.strftime('%H:%M:%S')
    try:
        expirationActivationCode = email_details["oldEmailCodeExpires"].strftime('%H:%M:%S')
        if expirationActivationCode > time_str and email_details["canChangeEmail"]:
            if email_details["oldEmailCode"] == oldcode:
                newcode = verificationCode()
                dct = {
                    "newEmail": newEmail,
                    "newEmailCode": newcode, 
                    "newEmailCodeExpires": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                    }
                email_details.update(dct)
                user.save()
                send_email(newEmail, newcode)
                return Response(
                    {
                        "status":"success",
                        "value":{"userId":user.id},
                        "message":"Number verified successfully"
                    }, status=200
                    )
            else:
                return Response (
                                {
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
    except KeyError:
        return Response({
                        "status": "error",
                        "value": None,
                        "message": "You have not sent an email"
                        }, status=400)
    

def verifyAndChangeNewEmail(request):
    userId = request.data.get("userId")
    code = request.data.get("number")
    user = Users.objects.get(id=userId)
    email_details = user.email_details
    current_time = datetime.datetime.now()
    time_str = current_time.strftime('%H:%M:%S')
    try:
        expirationActivationCode = email_details["newEmailCodeExpires"].strftime('%H:%M:%S')
        if expirationActivationCode > time_str:
            if email_details["newEmailCode"] == code:
                user.email = email_details["newEmail"]
                user.email_details = {}
                user.save()
                return Response(
                    {
                    "status":"success",
                    "value":{"userId":user.id},
                    "message":"Email confirmation sent successfully"
                    }, status=200
                    )
            else:
                return Response (
                                {
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
    except KeyError:
        return Response({
                        "status": "error",
                        "value": None,
                        "message": "You have not sent an email"
                        }, status=400)