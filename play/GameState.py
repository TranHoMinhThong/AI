import numpy as np
import copy
import json
import random
from operator import itemgetter
from django.http import JsonResponse

inf = 10**9


class State:
    def __init__(self, matrix=np.zeros((6, 6)), length=-1, freeCell=[(i, j) for i in range(6) for j in range(6)], freeAdjacentCell=set(), player=1, latestCheckedCell=None):
        #  0: free box
        #  1: human
        # -1: the robot
        self.matrix = matrix
        self.length = length+1
        self.freeCell = freeCell
        self.freeAdjacentCell = freeAdjacentCell
        self.latestCheckedCell = latestCheckedCell
        self.status = 0
        if self.latestCheckedCell and player:
            self.matrix[self.latestCheckedCell] = player
            self.freeCell.remove(latestCheckedCell)
            if latestCheckedCell in self.freeAdjacentCell:
                self.freeAdjacentCell.remove(latestCheckedCell)
            u = self.latestCheckedCell[0]
            v = self.latestCheckedCell[1]
            addedCell = {(i, j) for i in [u-1, u, u+1] for j in [v-1, v, v+1]
                         if 0 <= i < 6 and 0 <= j < 6 and not(i == u and j == v)}
            addedCell = {e for e in addedCell if self.matrix[e] == 0}
            self.freeAdjacentCell = self.freeAdjacentCell | addedCell
            self.status = self.check(self.latestCheckedCell)

    def check(self, cell):

        if self.matrix[cell] == 0:
            return 0
        # check all row, col, diag cotain the cell
        # check row:
        i = cell[0]
        j = cell[1]-1
        s1 = 0
        while j >= 0:
            if self.matrix[i, j] == self.matrix[cell]:
                s1 += 1
            else:
                break
            j -= 1
        j = cell[1]+1
        s2 = 0
        while j < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s2 += 1
            else:
                break
            j += 1
        if s1+s2+1 >= 4:
            return self.matrix[cell]
        # check col:
        i = cell[0]-1
        j = cell[1]
        s1 = 0
        while i >= 0:
            if self.matrix[i, j] == self.matrix[cell]:
                s1 += 1
            else:
                break
            i -= 1
        i = cell[0]+1
        s2 = 0
        while i < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s2 += 1
            else:
                break
            i += 1
        if s1+s2+1 >= 4:
            return self.matrix[cell]
        # check diag:
        i = cell[0]-1
        j = cell[1]-1
        s1 = 0
        while 0 <= i < 6 and 0 <= j < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s1 += 1
            else:
                break
            i -= 1
            j -= 1
        i = cell[0]+1
        j = cell[1]+1
        s2 = 0
        while 0 <= i < 6 and 0 <= j < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s2 += 1
            else:
                break
            i += 1
            j += 1
        if s1+s2+1 >= 4:
            return self.matrix[cell]
        i = cell[0]-1
        j = cell[1]+1
        s1 = 0
        while 0 <= i < 6 and 0 <= j < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s1 += 1
            else:
                break
            i -= 1
            j += 1
        i = cell[0]+1
        j = cell[1]-1
        s2 = 0
        while 0 <= i < 6 and 0 <= j < 6:
            if self.matrix[i, j] == self.matrix[cell]:
                s2 += 1
            else:
                break
            i += 1
            j -= 1

        if s1+s2+1 >= 4:
            return self.matrix[cell]
        else:
            return 0

    def getFreeCell(self):
        return self.freeCell

    def getFreeAdjacentCell(self):
        return self.freeAdjacentCell

    def tickCell(self, player, cell):
        # player: 1 for the human, -1 for robot
        # cell: tuple
        childState = State(np.copy(self.matrix), self.length,
                           copy.deepcopy(self.freeCell), copy.deepcopy(self.freeAdjacentCell), player, cell)
        return childState

    def __numOfBlocks(self, row, column, count, type):
        '''
        This function is used by evaluation function to calculate blocks
        at the begin and the end of consecutive human's moves
        type: 1 is row, 2 is column, 3 is diagonal from left to right, 4 is diagonal from right to left
        '''
        ret = 0
        if (type == 1):
            if (column == 6) or (self.matrix[row, column] == -1):
                ret += 1
            if (column - count - 1) < 0 or (self.matrix[row, column - count - 1] == -1):
                ret += 1
        elif (type == 2):
            if (row == 6) or (self.matrix[row, column] == -1):
                ret += 1
            if (row - count - 1 < 0) or (self.matrix[row - count - 1, column] == -1):
                ret += 1
        elif (type == 3):
            if (row == 6) or (column == 6) or (self.matrix[row, column] == -1):
                ret += 1
            if (column - count - 1 < 0) or (row - count - 1 < 0) or (self.matrix[row - count - 1, column - count - 1] == -1):
                ret += 1
        elif (type == 4):
            if (row == 6) or (column < 0) or (self.matrix[row, column] == -1):
                ret += 1
            if (row - count - 1 < 0) or (column + count + 1 >= 6) or (self.matrix[row - count - 1, column + count + 1] == -1):
                ret += 1
        return ret

    def evaluation(self):
        numOfMandatoryMoves = 0
        def updateNumOfMandatoryMoves(row, column, count, type):
            numOfBlocks = self.__numOfBlocks(row, column, count, type)
            if count == 2 and numOfBlocks == 0:
                return 1
            elif count == 3 and numOfBlocks == 1:
                return 1
            elif count == 3 and numOfBlocks == 0:
                # This must be return 2 but adjust this to higher to prioritize this case
                return 4
            elif count >= 4:
                return inf
            return 0

        # check rows
        for i in range(6):
            count = 0
            for j in range(6):
                if self.matrix[i, j] == 1:
                    count += 1
                elif count != 0:    # reach the end of consecutive moves
                    ret = updateNumOfMandatoryMoves(i, j, count, 1)
                    if ret == inf:
                        return inf
                    else:
                        numOfMandatoryMoves += ret
                    count = 0
            if count != 0:
                ret = updateNumOfMandatoryMoves(i, 6, count, 1)
                if ret == inf:
                    return inf
                else:
                    numOfMandatoryMoves += ret

        # check columns
        for i in range(6):
            count = 0
            for j in range(6):
                if self.matrix[j, i] == 1:
                    count += 1
                elif count != 0:    # reach the end of consecutive moves
                    ret = updateNumOfMandatoryMoves(j, i, count, 2)
                    if ret == inf:
                        return inf
                    else:
                        numOfMandatoryMoves += ret
                    count = 0
            if count != 0:
                ret = updateNumOfMandatoryMoves(6, i, count, 2)
                if ret == inf:
                    return inf
                else:
                    numOfMandatoryMoves += ret

        # check diagonal from left to right
        startPoints = [(2,0), (1,0), (0,0), (0,1), (0,2)]
        for point in startPoints:
            i, j = point
            count = 0
            while (i < 6 and j < 6):
                if self.matrix[i, j] == 1:
                    count += 1
                elif count != 0:    # reach the end of consecutive moves
                    ret = updateNumOfMandatoryMoves(i, j, count, 3)
                    if ret == inf:
                        return inf
                    else:
                        numOfMandatoryMoves += ret
                    count = 0
                i += 1
                j += 1
            if count != 0:
                ret = updateNumOfMandatoryMoves(i, j, count, 3)
                if ret == inf:
                    return inf
                else:
                    numOfMandatoryMoves += ret

        # check diagonal from left to right
        startPoints = [(1,5), (2,5), (0,3), (0,4), (0,5)]
        for point in startPoints:
            i, j = point
            count = 0
            while (i < 6 and j >= 0):
                if self.matrix[i, j] == 1:
                    count += 1
                elif count != 0:    # reach the end of consecutive moves
                    ret = updateNumOfMandatoryMoves(i, j, count, 4)
                    if ret == inf:
                        return inf
                    else:
                        numOfMandatoryMoves += ret
                    count = 0
                i += 1
                j -= 1
            if count != 0:
                ret = updateNumOfMandatoryMoves(i, j, count, 4)
                if ret == inf:
                    return inf
                else:
                    numOfMandatoryMoves += ret

        return numOfMandatoryMoves * 10**6


class Node:
    def __init__(self, cell=None, point=None):
        self.cell = cell
        self.children = []
        self.point = point

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class result:
    def __init__(self, status, node=None, robotCell=None):
        self.status = status
        self.robotCell = robotCell
        self.node = node

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def MaxHumanPrunning(state, subroot, depth, ab, maxDepth=2):
    # ab=[alpha,beta]
    if(state.length==6 and state.latestCheckedCell==(3,3)):
        print('e',state.status)
    if not state.status == 0:
        return inf if state.status == 1 else -inf
    if depth == maxDepth:
        subroot.point = state.evaluation()
        return subroot.point
    subroot.point = -inf
    for freeCell in state.getFreeAdjacentCell():
        newNode = Node(freeCell)
        newNode.point = MinRobotPrunning(
            state.tickCell(1, freeCell), newNode, depth+1, ab, maxDepth)
        subroot.children.append(newNode)
        subroot.point = max(subroot.point, newNode.point)
        ab[0] = max(ab[0], subroot.point)
        if subroot.point >= ab[1] and depth > 0:
            break

    subroot.children.sort(reverse=True, key=lambda e: e.point)
    return subroot.point


def MinRobotPrunning(state, subroot, depth, ab, maxDepth=2):
    # ab=[alpha,beta]
    if not state.status == 0:
        return inf if state.status == 1 else -inf
    if depth == maxDepth:
        subroot.point = state.evaluation()
        return subroot.point
    subroot.point = inf
    for freeCell in state.getFreeAdjacentCell():
        newNode = Node(freeCell)
        newNode.point = MaxHumanPrunning(state.tickCell(-1,
                                                        freeCell), newNode, depth+1, ab, maxDepth)
        subroot.children.append(newNode)
        subroot.point = min(subroot.point, newNode.point)
        ab[1] = min(ab[1], subroot.point)
        if subroot.point <= ab[0] and depth > 0:
            break

    subroot.children.sort(reverse=False, key=lambda e: e.point)
    # if depth==0:
    #     for e in subroot.children:
    #         print('a',e.cell,e.point)
    #         for ec in e.children:
    #             print('aa',ec.cell, ec.point)
    return subroot.point

count = 0

def tickCell_AlphaBetaPrunning(state, index, request):
    global count
    a = int(request.POST['a'])
    b = int(request.POST['b'])
    if (a != -1 and b != -1):
        count += 1
        cell = (a, b)
        print(cell)
        # check if alresdy win
        state[index] = state[index].tickCell(1, cell)
        print(state[index].status)
        if state[index].status == 1:
            return JsonResponse(result(status=1).toJson(), safe=False)

        node = Node(cell)
        ab = [-inf, inf]
        MinRobotPrunning(state[index], node, 0, ab)
        cell = node.children[0].cell
        state[index] = state[index].tickCell(-1, cell)
        if state[index].status == -1:
            return JsonResponse(result(status=-1, robotCell=cell).toJson(), safe=False)

        node = Node(cell)
        ab = [-inf, inf]
        MaxHumanPrunning(state[index], node, 0, ab)
        return JsonResponse(result(status=0, robotCell=cell, node=node).toJson(), safe=False)
    else:
        state[index] = State()
        return JsonResponse(result(status=1).toJson(), safe=False)
#01,20

# a=State().tickCell(1,(0,0)).tickCell(-1,(0,1)).tickCell(1,(1,1)).tickCell(-1,(2,0)).tickCell(1,(2,2)).tickCell(1,(3,3))
# print(a.status)