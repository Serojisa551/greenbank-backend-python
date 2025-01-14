from authentication.middleware import UsersAuthenticationMiddleware
from django.http import JsonResponse
import json

class AccountMiddelware:
    def __init__(self, get_response=None):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            path = request.path
            parts = path.split('/')
            id = parts[-1]
            data = json.loads(request.body.decode("utf-8"))
            if request.path.startswith(f"/aip/accounts/{id}"):
                self.checkingAccountAndCard(id, "account")
            if request.path.startswith(f"/aip/cards/{id}"):
                self.checkingAccountAndCard(id, "card")
            elif (request.path.startswith("/api/accounts/") or
                  request.path.startswith("/api/cards/")):
                if request.method == "POST":
                    userId = data.get("userId")
                    UsersAuthenticationMiddleware.checkingUser(userId)
                    
        except json.JSONDecodeError:
            pass
        except ValueError as e:
            return JsonResponse(
                {
                "status": "error",
                "value": None,
                "message": f"{e}"}, status=400
            )
        response = self.get_response(request)
        return response

    def checkingAccountAndCard(self, userId, flag):
        try:
            if flag == "account":
                account = Accounts.objects.get(id=userId)
                if account.is_deleted:
                    raise ValueError("Account not found!")
            elif flag == "card":
                card = Cards.objects.get(id=userId)
                if card.is_deleted:
                    raise ValueError("Card not found!")
        except Accounts.DoesNotExist:
            raise ValueError("Such a account does not exist")
        except Cards.DoesNotExist:
            raise ValueError("Such a card does not exist")