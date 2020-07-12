from django.shortcuts import render
from django.http import HttpResponse
from .GameState import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

state = [State()]
ab = [-9999999999999999999, 9999999999999999999]


def index(request):
    state[0] = State()
    return render(request, 'pages/play.html')


@csrf_exempt
def tickCell(request):
    if request.method == 'POST':
        return tickCell_AlphaBetaPrunning(state,request)