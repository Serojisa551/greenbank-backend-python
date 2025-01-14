from authentication.utils import verificationCode, send_email
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from authentication.models import Users
from rest_framework import status
import datetime

def resetPasswordSendEmail(request):
    email = request.data.get("email")
    user = Users.objects.get(email=email)
    code = verificationCode()
    user.resetPassword =  {
        "EmailCode": code,
        "EmailCodeExpires": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "canChangeEmail": False
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
    

def resetPasswordVerifyEmail(request):
    userId = request.data.get("userId")
    code = request.data.get("number")
    user = Users.objects.get(id=userId)
    resetPassword = user.resetPassword
    current_time = datetime.datetime.now()
    time_str = current_time.strftime('%H:%M:%S')
    try:
        expirationActivationCode = resetPassword["EmailCodeExpires"].strftime('%H:%M:%S')
        if expirationActivationCode > time_str:
            if resetPassword["EmailCode"] == code:
                resetPassword["canChangeEmail"] = True
                user.save()
                return Response(
                    {
                        "status":"success",
                        "value":{"userId":user.id},
                        "message":"Email confirmation sent successfully"
                    }, status=200
                    )
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
    except KeyError:
        return Response({
                            "status": "error",
                            "value": None,
                            "message": "You have not sent an email"
                        }, status=400)
       
    
def changePassword(request):
    userId = request.data.get("userId")
    password = request.data.get("password")
    user = Users.objects.get(id=userId)
    try:
        if user.resetPassword["canChangeEmail"]:
            user.password = make_password(password)
            user.resetPassword = {}
            user.save()
        return Response({
            "status": "success",
            "value": {},
            "message": "Password reset was successful"
        })
    except KeyError:
        return Response({"error":"You have not sent an email"}, status=400)