from rest_framework.decorators import api_view, parser_classes
from authentication.serializers import CheckActivCodeSerializer
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from django.http.response import JsonResponse
from rest_framework.response import Response
from django.shortcuts import render
from biznesLogic.users import *
from .utils import getPayload
from drf_yasg import openapi


@swagger_auto_schema(
    method="PATCH",
    request_body=ChnageUserDataSerializer,
    manual_parameters=[
        openapi.Parameter(
            "userId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
    consumes=['multipart/form-data'],
)
@swagger_auto_schema(
    method="DELETE",
    manual_parameters=[
        openapi.Parameter(
            "userId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "userId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET","DELETE", "PATCH"])
@parser_classes([MultiPartParser])
def changeAndGettingAandDelete(request, userId):
    data = Response()
    if request.method == "GET":
        data = get_user(request, userId)
    elif request.method == "DELETE":
        data = deleteUser(request, userId)
    elif request.method == "PATCH":
        data = changeUserData(request, userId)
    return data


@api_view(["GET"])
def getAllUsers(request):
    return gettingAllUsers(request)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "ImgId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET"])
def getUserImg(request, ImgId):
    payload = getPayload(request.COOKIES)
    if payload["is_superuser"] == True:
        data = gettingUserImg(request, ImgId)
    else:
        if payload["id"] == ImgId:
            data = gettingUserImg(request, ImgId)
        else:
            return Response(
                            {
                                "status": "error",
                                "value": None,
                                "message": "User can access to data connected to him"
                            }, status=403
                        )
    return data


@swagger_auto_schema(
    method="PATCH",
    request_body=PasswordChangeSerializer,
)
@api_view(["PATCH"])
def changePassword(request):
    return changingPassword(request)


@swagger_auto_schema(
    method="POST",
    request_body=VerifyAndWriteNewEmailSerializer
)
@swagger_auto_schema(
    method="PATCH",
    request_body=CheckActivCodeSerializer,
)
@api_view(["PATCH", "POST"])
def newEmail(request):
    data = Response()
    if request.method == "PATCH":
        data = verifyAndChangeNewEmail(request)
    elif request.method == "POST":
        data = verifyAndWriteNewEmail(request)
    return data

@swagger_auto_schema(
    method="PATCH",
    request_body=SendCurrentEmailSerializer,
)
@api_view(["PATCH"])
def changeEmail(request):
    return sendingCurrentEmail(request)