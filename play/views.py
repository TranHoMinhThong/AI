from django.shortcuts import render
from django.http import HttpResponse
from .GameState import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

globalState=[]

def index(request):
    if (not (request.session.get("state", False))) or (request.session["state"] >= len(globalState)):
        request.session["state"] = len(globalState)
        globalState.append(State())
    else:
        globalState[request.session["state"]] = State()

    return render(request,'pages/play.html')

@csrf_exempt
def tickCell(request):
    if request.method=='POST':
        # assume that session state is already available
        index = request.session["state"]

        a=int(request.POST['a'])
        b=int(request.POST['b'])
        if a != -1 and b != -1:
            cell=(a,b)
            print(cell)
            # check if already win
            globalState[index]=globalState[index].tickCell(1,cell)
            print(globalState[index].status)
            if globalState[index].status==1:
                return JsonResponse(result(status=1).toJson(),safe=False)

            node=Node(cell)
            MinRobot(globalState[index],node,0,3)
            cell=node.children[0].cell
            globalState[index]=globalState[index].tickCell(-1,cell)
            if globalState[index].status==-1:
                return JsonResponse(result(status=-1,robotCell=cell).toJson(),safe=False)

            node=Node(cell)
            MaxHuman(globalState[index],node,0,3)
            return JsonResponse(result(status=0,robotCell=cell,node=node).toJson(),safe=False)
        else:
            globalState[request.session["state"]]=State()
            return JsonResponse(result(status=1).toJson(),safe=False)
