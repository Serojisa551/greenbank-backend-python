from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .utils import currencys_tpl


@api_view(["GET"])
def getUSD(request):
    return Response(currencys_tpl[0])


@api_view(["GET"])
def getRUB(request):
    return Response(currencys_tpl[1])


@api_view(["GET"])
def getEUR(request):
    return Response(currencys_tpl[2])


@api_view(["GET"])
def getAMD(request):
    return Response(currencys_tpl[3])


@api_view(["GET"])
def getAll(request):
    return Response(currencys_tpl)
