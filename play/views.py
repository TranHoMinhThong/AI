from django.shortcuts import render
from django.http import HttpResponse
from .GameState import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

state=[State()]

def index(request):
   return render(request,'pages/play.html')

@csrf_exempt
def tickCell(request):
    if request.method=='POST':
        
        a=int(request.POST['a'])
        b=int(request.POST['b'])
        cell=(a,b)
        print(cell)
        state[0]=state[0].tickCell(1,cell)
        if state[0].check(cell)==1:
            return JsonResponse(result(1).toJson(),safe=False)

        node=Node(cell)
        MinRobot(state[0],node,0,3)
        cell=node.children[0].cell
        state[0]=state[0].tickCell(1,cell)
        if state[0].check(cell)==-1:
            return JsonResponse(result(status=-1,robotCell=cell).toJson(),safe=False)
        
        MaxHuman(state[0],node,0,3)
        return JsonResponse(result(status=0,robotCell=cell,node=node).toJson(),safe=False)
    