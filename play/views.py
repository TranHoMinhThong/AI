from django.shortcuts import render
from django.http import HttpResponse
from .GameState import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

state=[State()]

def index(request):
    state[0]=State()
    return render(request,'pages/play.html')

@csrf_exempt
def tickCell(request):
    if request.method=='POST':
        
        a=int(request.POST['a'])
        b=int(request.POST['b'])
        if a != -1 and b != -1:
            cell=(a,b)
            print(cell)
            # check if alresdy win
            state[0]=state[0].tickCell(1,cell)
            print(state[0].status)
            if state[0].status==1:
                return JsonResponse(result(status=1).toJson(),safe=False)

            node=Node(cell)
            MinRobot(state[0],node,0,3)
            cell=node.children[0].cell
            state[0]=state[0].tickCell(-1,cell)
            if state[0].status==-1:
                return JsonResponse(result(status=-1,robotCell=cell).toJson(),safe=False)
            
            node=Node(cell)
            MaxHuman(state[0],node,0,3)
            return JsonResponse(result(status=0,robotCell=cell,node=node).toJson(),safe=False)
        else:
            state[0]=State()
            return JsonResponse(result(status=1).toJson(),safe=False)
    