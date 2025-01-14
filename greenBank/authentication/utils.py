from authentication.models import Users, AccountIds, CardIds
from users.serializers import UserGettingSerializer
from django_ratelimit.decorators import ratelimit
from accounts.utils import generatedAccountNumber
from email.mime.multipart import MIMEMultipart
from accounts.models import Accounts
from email.mime.text import MIMEText
from django.http import JsonResponse
from django.conf import settings
from random import randint
from .models import Token
from .models import *
import jwt, datetime
import smtplib
import os


def createRefreshToken(user):
    payload = {
        "id": user.id,
        "is_superuser": user.is_superuser,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "phone": user.phone,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1000000),
        "iat": datetime.datetime.utcnow(),
    }

    refreshToken = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    if Token.checkingToken(user, refreshToken):
        Token.objects.create(token=refreshToken, userId=user)

    return refreshToken


def createAccessToken(user):
    payload = {
        "id": user.id,
        "is_superuser": user.is_superuser,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "phone": user.phone,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        "iat": datetime.datetime.utcnow(),
    }

    accessToken = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return accessToken


def createAccountForRergister():
    accountNumber = generatedAccountNumber()
    account = Accounts(
        accountType="current",
        currency="AMD",
        accountNumber=accountNumber,
        isDefault=True,
    )
    account.save()

    return accountNumber


def accountIdSaver(email, accountNumber):
    try:
        user = Users.objects.get(email=email)
        account = Accounts.objects.get(accountNumber=accountNumber)
        accountId = AccountIds(user=user, account=account)
        accountId.save()
        return account
    except Users.DoesNotExist:
        return {
                "status":"error",
                "value":None,
                "message":f"A user with this email does not exist '{email}'"
                }
    except Accounts.DoesNotExist:
        return {
                "status":"error",
                "value":None,
                "message":f"A account with this number does not exist '{accountNumber}'"
                }
        

def verificationCode():
    code = ""
    for i in range(4):
        code += str(randint(0, 9))
    return code


def send_email(email, code):  
    html_content = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; text-align: center; color: #333; background-color: #F7F7F7; padding: 40px;">
    <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
      <h1 style="color: #4CAF50; margin-bottom: 20px;">Email Verification Needed</h1>
      <p style="font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
        Thank you for registering with us. Please enter the following verification code to activate your account.
      </p>
      <div style="background-color: #E7F4E4; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
        <h2 style="margin: 0; font-size: 24px; color: #388E3C;">{code}</h2>
      </div>
      <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        If you did not request this verification, please ignore this email.
      </p>
      <footer style="text-align: center; padding-top: 20px; font-size: 12px; color: #777;">
        &copy; Your Company Name. All rights reserved.
      </footer>
    </div>
  </div>
        </body>
    </html>
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = os.getenv('EMAIL_USERNAME')
    message["To"] = email
    part = MIMEText(html_content, "html")
    message.attach(part)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(message["From"], os.getenv('EMAIL_PASSWORD'))
    server.sendmail(message["From"], email, message.as_string())
    server.quit()
    print(f"Email sent successfully to '{email}'")


def rate_limit_exceeded_handler(request, exception):
    return JsonResponse({'error': 'Try it later'}, status=429)


def getUserAccountsAndCards(userId):
    user =  Users.objects.get(id=userId)
    accounts = AccountIds.objects.filter(user_id=userId)
    cards = CardIds.objects.filter(user_id=userId)
        
    lsAccount = []
    lsCard = []
    dct = {"accounts":lsAccount, "cards":lsCard}
    if len(accounts):
        for obj in accounts:
            lsAccount.append(obj.account.id)
    if len(cards):
        for obj in cards:
            lsCard.append(obj.card.id)
    serialized = UserGettingSerializer(user)
    userData = dict(serialized.data)
    userData.update(dct)
    return userData