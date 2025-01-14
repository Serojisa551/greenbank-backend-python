from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from users.utils import getPayload, validateName
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
from .models import Users
import jwt, datetime
import json
import re

class BearerTokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def validate_access_token(self, access_token):
        if access_token[:6] == "Bearer":
            access_token = access_token.split(" ")[1]
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = payload["id"]

            if user_id is None:
                raise AuthenticationFailed()

            return payload
        except AuthenticationFailed:
            return JsonResponse({
                            "status":"error",
                            "value": None,
                            "message": "Invalid token: Missing user_id"
                            }, status=401)
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                            "status":"error",
                            "value": None,
                            "message": "Token has expired"
                            }, status=401)

    def __call__(self, request):
        if (
            request.path.startswith("/api/auth/forgetPassword")
            or request.path.startswith("/api/auth/resetPassword")
            or request.path.startswith("/api/accounts/")
            or request.path.startswith("/api/cards/")
            or request.path.startswith("/api/transaction/")
            or request.path.startswith("/api/users/")
        ):
            try:
                access_token = request.headers["Authorization"]
                user_payload = self.validate_access_token(access_token)

                user_id = user_payload.get("id")                
                user = Users.objects.get(id=user_id)

                request.user = user
            except Users.DoesNotExist:
                return JsonResponse(
                        {
                        "status":"error",
                        "value":None,
                        "message":"Users matching query does not exist."
                        }, status=400
                )
            except KeyError:
                return JsonResponse(
                        {
                        "status":"error",
                        "value":None,
                        "message":"Refresh token is not valid"
                        }, status=401
                )
        response = self.get_response(request)
        return response


class UsersAuthenticationMiddleware:
    def __init__(self, get_response=None):
        super().__init__()
        self.get_response = get_response

    def __call__(self, request):
        try:
            path = request.path
            parts = path.split('/')
            userId = parts[-1]
            if request.path.startswith("/api/auth/"):
                data = json.loads(request.body.decode("utf-8"))
                if request.path.startswith("/api/auth/registration"):
                    firstName = data.get("firstName")
                    lastName = data.get("lastName")
                    birthday = data.get("birthday")
                    phone_number = data.get("phone")
                    password = data.get("password")
                    email = data.get("email")
                    validateName(firstName)
                    validateName(lastName)
                    self.is_valid_email(email)
                    self.check_password(password)
                    if not self.is_valid_phone_number(phone_number):
                        raise ValueError(f"Phone did not pass validation '{phone_number}'")         
                    self.is_valid_age(birthday)
                if request.path.startswith("/api/auth/login"):
                    email = data.get("email")
                    password = data.get("password")
                    self.authenticate_user(email, password)
                if (request.path.startswith("/api/auth/checkActiveCcode")
                    or request.path.startswith("/api/auth/refreshActivationCode")
                    ):
                    userId = data.get("userId")
                    try:
                        user = Users.objects.get(id=userId)
                        if user.is_active:
                            raise ValueError("This user has already been activated")
                    except Users.DoesNotExist:
                        raise ValueError("Such an user does not exist")
                if request.path.startswith("/api/auth/forgetPassword"):
                    if request.method == "PATCH":
                        userId = data.get("userId")
                        email = data.get("email")
                        payload = getPayload(request.COOKIES)
                        self.checkingUser(userId)
                        self.checkingEmailUser(userId, email, payload)
                    elif request.method == "POST":
                        userId = data.get("userId")
                        self.checkingUser(userId)
                if request.path.startswith("/api/auth/resetPassword"):
                    userId = data.get("userId")
                    password = data.get("password")
                    payload = getPayload(request.COOKIES)
                    self.checkingUser(userId)
                    self.verifyUserIdentifier(userId, payload)
                    self.check_password(password)
                if request.path.startswith(f"/api/auth/resetVerifyNumber/{userId}"):
                    self.checkingUser(userId)
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

    def authenticate_user(self, email, password):
        try:
            user = Users.objects.get(email=email)
            if user.is_deleted:
                raise ValueError("User not found!")

            if not check_password(password, user.password):
                raise ValueError("Incorrect password!")
        except Users.DoesNotExist:
            raise ValueError("Such an user does not exist")
    
    @staticmethod  
    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not bool(re.match(pattern, email)):
            raise ValueError(f"Invalid email address '{email}'.")
        
    @staticmethod
    def check_password(password):
        length = len(password)
        if type(password) != str:
            raise ValueError("Password must be a string")
        elif length == 0:
            raise ValueError("The password must not be empty")
        elif 8 > length or length > 30:
            raise ValueError(
                "The password must be shorter than 8 characters and no more than 30 characters"
            )
        is_upper = False
        for symbol in password:
            if symbol == " " or symbol == "\n" or symbol == "\t":
                raise ValueError("The password must not contain spaces")
            if symbol.isupper(): 
                is_upper = True
        if not is_upper:
            raise ValueError("The password must contain at least one capital letter")

    @staticmethod
    def is_valid_phone_number(phone_number):
        return bool(re.match(r"^\+374\d{8}$", phone_number))

    def extract_date_components(self, date_str):
        return list(map(int, date_str.split("-")))

    def is_valid_age(self, user_date_str):
        user_date = self.extract_date_components(user_date_str)
        current_date = self.extract_date_components(str(datetime.datetime.now().date()))

        user_age = current_date[0] - user_date[0]

        if user_age < 18:
            raise ValueError("User must be at least 18 years old.")
        elif user_age > 18:
            return True
        else:
            if current_date[1:] >= user_date[1:]:
                return True
            else:
                raise ValueError("User must be at least 18 years old.")

    @staticmethod
    def checkingUser(userId):
        try:
            user = Users.objects.get(id=userId)
            if user.is_deleted:
                raise ValueError("User not found!")
        except Users.DoesNotExist:
            raise ValueError("Such a user does not exist")
        
    @staticmethod
    def verifyUserIdentifier(userId, payload):
        if userId == payload["id"] or payload["is_superuser"] :
            is_valid = True
        else:
            raise ValueError("This user is not an admin and cannot give the ID of another user")
        return is_valid
        
    @staticmethod
    def checkingEmailUser(userId, email, payload):
        is_valid = False
        if not payload["is_superuser"]:
            is_valid = UsersAuthenticationMiddleware.verifyUserIdentifier(userId, payload)
        if payload["is_superuser"] or is_valid:
            user = Users.objects.get(id=userId)
            if str(user.email) != email:
                    raise ValueError(f"This email '{email}' does not belong to a user with an ID {userId}")
