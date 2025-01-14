from authentication.models import Users, CardIds, AccountIds
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from mongoengine.fields import Decimal128
from accounts.utils import decoding
from .serializers import *
import re


def deleteUserById(id):
    user = Users.objects.get(id=id)
    cards = CardIds.objects.filter(user=user)
    accounts = AccountIds.objects.filter(user=user)
    user.is_deleted = True
    user.save()
    for card in cards:
        card.card.is_deleted = True
        card.card.save()
    for account in accounts:
        account.account.is_deleted = True
        account.account.balance = Decimal128.to_decimal(account.account.balance)
        account.account.save()
    

def changingUserData(request, userId):
    filter_data = filterData(request.data)
    user = Users.objects.get(id=userId)
    for key, value in filter_data.items():    
        if value is not None:
            if key == "firstName":
                user.firstName = value
            elif key == "lastName":
                user.lastName = value
            elif key == "phone":
                user.phone = value
            elif key == "img":
                user.img = value
    user.save()


def checkPhone(phone):
    if not bool(re.match(r"^\+374\d{8}$", phone)):
        raise ValueError("Phone did not pass validation")
    if not Users.is_phone_unique(phone):
        raise ValueError("This phone number has already been registered")
    else:
        return True
    
    
def filterData(data):
    filtered_data = {}
    try:
        for key, value in data.items():
            if value is not None:
                if key == "firstName" or key == "lastName":
                    validateName(value)
                    filtered_data[key] = value
                elif key == "phone":
                    checkPhone(value)
                    filtered_data[key] = value
                elif key == "img":
                    filtered_data[key] = value
        return filtered_data
    except ValueError as e:
        return Response(
            {
            "status": "error",
            "value": None,
            "message": f"{e}"
            }, status=400)


# def f(userId):
#         user = Users.objects.get(id=userId)
#         image_data = user.img.read()
#         image_data_base64 = base64.b64encode(image_data).decode('utf-8')
#         return Response(
#             {
#                 "status": "success",
#                 "value": {
#                     "id": user.id,
#                     "type": "image/png",
#                     "imageData": image_data_base64
#                 },
#                 "message": "Image successfully returned"
#             }
#         )
        
        
def getPayload(cookies):
    print(cookies.get("refreshToken"))
    token = cookies.get("refreshToken")
    payload = decoding(token)
    return payload


def validateName(name):

    if not re.match(r"^[A-Z][a-zA-Z]{2,256}$", name):
        raise ValueError("The first or last name must begin with a capital letter")