from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework import status
from biznesLogic.transaction import *

@swagger_auto_schema(
    methods=["GET"],
    query_serializer=CreateQRSerializer,
)
@api_view(["GET"])
def createQRToken(request):
    return creatingQRToken(request)

@swagger_auto_schema(
    methods=["POST"],
    request_body=TransactionSerializer,
)
@api_view(["POST"])
def transaction(request):
    typeTransver = request.data.get("type")
    typeTransver = typeTransver.lower()
    if typeTransver == "phone":
        return EasyTransver(request)
    elif typeTransver == "qr_account" or typeTransver == "qr_card":
        return TransferToQR(request)
    elif typeTransver == "account":
        return accountToAccount(request)
    elif typeTransver == "card":
        return cardToCard(request)


@swagger_auto_schema(
    methods=["GET"],
    query_serializer=InputTransactionHistory,
)
@api_view(["GET"])
def getHistory(request):
    ls = processRequest(request)
    data = None
    page = checkPage(request)
    if page:
        return page
    if type(ls) != list:
        return ls
    if "isCredit" in ls:
        data = getTransactionHistoryByIsCredit(request)
    if "startDate" in ls or "endDate" in ls:
        if data:
            data = get_transaction_history_by_date(request, data)
        else:
            data = get_transaction_history_by_date(request)
    if "number" in ls:
        if data:
            data = get_transaction_history_by_number(request, data)
        else:
            data = get_transaction_history_by_number(request)
    if "miniAmount" in ls or "maxAmount" in ls:
        if data:
            data = getTransactionHistoryByAmount(request, data)
        else:
            data = getTransactionHistoryByAmount(request)
    if "isDone" in ls:
        if data:
            data = getTransactionHistoryByIsDone(request, data)
        else:
            data = getTransactionHistoryByIsDone(request)
    if "description" in ls:
        if data:
            data = getTransactionHistoryByDescriptions(request, data)
        else:
            data = getTransactionHistoryByDescriptions(request)
    if "userId" in ls:
        if data:
            data = gettiingHistory(request, data)
        else:
            data = gettiingHistory(request)
    if not data:
        return Response(
        {
            "status": "success",
            "value": {},
            "message": "transaction filtered successfully"
        },
        status=200
        )
    elif type(data) == list:
        return Response(
            {
                "status": "success",
                "value": {"transactions": data},
                "message": "transaction filtered successfully"
            },
            status=200
        )
    return data
