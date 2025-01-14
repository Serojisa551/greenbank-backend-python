from authentication.middleware import UsersAuthenticationMiddleware
from django.contrib.auth.hashers import check_password
from authentication.models import Users
from django.http import JsonResponse
from users.utils import getPayload
from django.conf import settings
from datetime import datetime
import jwt, datetime
import json
import re

class UsersMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        try:
            path = request.path
            parts = path.split('/')
            userId = parts[-1]
            if request.path.startswith("/api/users/"):
                if 'application/json' in request.content_type:
                    data = json.loads(request.body.decode("utf-8"))
                if "/api/users/" == path:
                    i = ""
                elif request.path.startswith("/api/users/changePassword"):
                    dct = {
                        "oldPassword": data.get("oldPassword"),
                        "newPassword": data.get("newPassword"),
                        "confirmNewPassword": data.get("confirmNewPassword")
                    }
                    self.checkingPassword(request, dct)
                elif request.path.startswith("/api/users/changeEmail"):
                    userId = data.get("userId")
                    email = data.get("email")
                    payload = getPayload(request.COOKIES)
                    UsersAuthenticationMiddleware.checkingUser(userId)
                    UsersAuthenticationMiddleware.checkingEmailUser(userId, email, payload)
                elif request.path.startswith("/api/users/newEmail"):
                    if request.method == "PATCH":
                        userId = data.get("userId")
                        UsersAuthenticationMiddleware.checkingUser(userId)
                    elif request.method == "POST":
                        userId = data.get("userId")
                        newEmail = data.get("newEmail")
                        UsersAuthenticationMiddleware.checkingUser(userId)
                        UsersAuthenticationMiddleware.is_valid_email(newEmail)
                        if not Users.is_email_unique(newEmail):
                            raise ValueError("This email has already been registered")
                elif request.path.startswith(f"/api/users/{userId}"):
                    UsersAuthenticationMiddleware.checkingUser(userId)
                elif request.path.startswith(f"/api/users/imge/{userId}"):
                    UsersAuthenticationMiddleware.checkingUser(userId)
                    self.userHasImg(userId)
        except json.JSONDecodeError:
            pass
        except ValueError as e:
            return JsonResponse({
                            "status":"error",
                            "value": None,
                            "message": f"{e}"
                            }, status=400)
        response = self.get_response(request)
        return response
    
    def userHasImg(self, userId):
        user = Users.objects.get(id=userId)
        if user.img == "":
            raise ValueError("User has not image")

    def checkingPassword(self, request, dct):
        payload = getPayload(request.COOKIES)
        user = Users.objects.get(id=payload["id"])
        oldPassword = dct["oldPassword"]
        newPassword = dct["newPassword"]
        confirmNewPassword = dct["confirmNewPassword"]
        if not check_password(oldPassword, user.password):
            raise ValueError("Incorrect password!")
        UsersAuthenticationMiddleware.check_password(newPassword)
        UsersAuthenticationMiddleware.check_password(confirmNewPassword)
        if newPassword != confirmNewPassword:
            raise ValueError("Passwords don't match")
        if oldPassword == newPassword:
            raise ValueError("The old password and the new password must not match")