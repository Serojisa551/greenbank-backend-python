from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from biznesLogic.cards import *
from drf_yasg import openapi
from .serializers import *



@swagger_auto_schema(
    methods=["POST"],
    request_body=WriteCreateCardSerializer,
)
@api_view(["POST", "GET"])
def createAndGetting(request):
    total = Response()
    if request.method == "POST":
        total = createCard(request)
    elif request.method == "GET":
        total = getUserCards(request)
    return total


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "cardId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@swagger_auto_schema(
    method="patch",
    request_body=UpdateCardNameSerializer,
    manual_parameters=[
        openapi.Parameter(
            "cardId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@swagger_auto_schema(
    method="delete",
    manual_parameters=[
        openapi.Parameter(
            "cardId",
            openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET", "PATCH", "DELETE"])
def changeAndGettingAandDelete(request, cardId):
    total = Response()
    if request.method == "PATCH":
        total = updateCardName(request, cardId)
    elif request.method == "GET":
        total = getCardById(request, cardId)
    elif request.method == "DELETE":
        total = deleteCard(request, cardId)
    return total
