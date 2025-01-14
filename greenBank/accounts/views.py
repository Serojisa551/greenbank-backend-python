from drf_spectacular.utils import extend_schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from biznesLogic.accounts import *
from drf_yasg import openapi
from .serializers import *


@swagger_auto_schema(
    methods=["GET"],
    operation_description="Endpoint to retrieve all games.",
)
@swagger_auto_schema(
    methods=["POST"],
    request_body=WriteCreateAccountSerializer,
    operation_description="Endpoint to add a new game.",
)
@api_view(["POST", "GET"])
def createAndGetting(request):
    total = Response()
    if request.method == "POST":
        total = createAccount(request)
    elif request.method == "GET":
        total = getUserAccounts(request)
    return total


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "accountId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@swagger_auto_schema(
    method="patch",
    request_body=UpdateAccountNameSerializer,
    manual_parameters=[
        openapi.Parameter(
            "accountId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@swagger_auto_schema(
    method="delete",
    manual_parameters=[
        openapi.Parameter(
            "accountId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET", "PATCH", "DELETE"])
def changeAndGettingAandDelete(request, accountId):
    total = Response()
    if request.method == "PATCH":
        total = updateAccountName(request, accountId)
    elif request.method == "GET":
        total = getAccountById(request, accountId)
    elif request.method == "DELETE":
        total = deleteAccount(request, accountId)
    return total
