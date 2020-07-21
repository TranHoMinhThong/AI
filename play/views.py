from django.shortcuts import render
from django.http import HttpResponse
from .GameState import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

globalState=[]
ab = [-inf, inf]


def index(request):
	if (not (request.session.get("state", False))) or (request.session["state"] >= len(globalState)):
		request.session["state"] = len(globalState)
		globalState.append(State())
	else:
		globalState[request.session["state"]] = State()

	return render(request, 'pages/play.html')

@csrf_exempt
def tickCell(request):
	if request.method == 'POST':
		index = request.session["state"]
		if request.POST['mode'] == 0:
			return tickCell_Minimax(globalState, request)			
		else:
			print(1)
			return tickCell_AlphaBetaPrunning(globalState, index, request)