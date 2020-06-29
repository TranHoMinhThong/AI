import numpy as np
import copy
import json


class State:
    def __init__(self, matrix=np.zeros((6, 6)), length=0, freeCell=[(i, j) for i in range(6) for j in range(6)],freeAdjacentCell=set()):
        #  0: free box
        #  1: human
        # -1: the robot
        self.matrix = matrix
        self.length = length
        self.freeCell = freeCell
        self.freeAdjacentCell=freeAdjacentCell

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
        h = cell[1]+1
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
        j = cell[0]-1
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
                           copy.deepcopy(self.freeCell),copy.deepcopy(self.freeAdjacentCell))
        childState.matrix[cell] = player
        childState.length += 1
        childState.freeCell.remove(cell)
        if cell in childState.freeAdjacentCell:
            childState.freeAdjacentCell.remove(cell)
        u=cell[0]
        v=cell[1]
        addedCell={(i,j) for i in [u-2,u-1,u+1,u+2] for j in [v-2,v-1,v+1,v+2] if 0<=i<6 and 0<=j<6 }
        addedCell={e for e in addedCell if self.matrix[e]==0}
        childState.freeAdjacentCell=childState.freeAdjacentCell|addedCell
        return childState


class Node:
    def __init__(self, cell=None, point=None):
        self.cell = cell
        self.children = []
        self.point = point

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def MaxHuman(state, subroot, depth, maxDepth=3):
    if not subroot.cell is None:
        i = state.check(subroot.cell)
        if not i == 0:
            subroot.point = i/state.length
            return subroot.point
    if depth == maxDepth:
        subroot.point = 0
        return 0
    subroot.point = -999999999999999999
    for freeCell in state.getFreeCell():
        newNode = Node(freeCell)
        newNode.point = MinRobot(
            state.tickCell(-1, freeCell), newNode, depth+1, maxDepth)
        subroot.children.append(newNode)
        subroot.point = max(subroot.point, newNode.point)
    subroot.children.sort(reverse=True,key=lambda e: e.point)
    return subroot.point


def MinRobot(state, subroot, depth, maxDepth=3):
    if not subroot.cell is None:
        i = state.check(subroot.cell)
        if not i == 0:
            subroot.point = i/state.length
            return subroot.point
    if depth == maxDepth:
        subroot.point = 0
        return 0
    subroot.point = 999999999999999999
    for freeCell in state.getFreeAdjacentCell():
        newNode = Node(freeCell)
        newNode.point = MaxHuman(state.tickCell(1,
                                                freeCell), newNode, depth+1, maxDepth)
        subroot.children.append(newNode)
        subroot.point = min(subroot.point, newNode.point)
    subroot.children=[min(subroot.children,key=lambda e: e.point)]
    return subroot.point

class result:
    def __init__(self, status, node=None,robotCell=None):
        self.status=status
        self.robotCell=robotCell
        self.node=node

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)