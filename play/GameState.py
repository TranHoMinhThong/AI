import numpy as np
import copy
import json
import random
from operator import itemgetter


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


class Node:
    def __init__(self, cell=None, point=None):
        self.cell = cell
        self.children = []
        self.point = point

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


def MaxHuman(state, subroot, depth, maxDepth=3):
    if not state.status == 0:
        subroot.point = state.status*10
        return subroot.point
    if depth == maxDepth:
        subroot.point = 0
        return 0
    subroot.point = -999999999999999999
    for freeCell in state.getFreeCell():
        newNode = Node(freeCell)
        newNode.point = MinRobot(
            state.tickCell(1, freeCell), newNode, depth+1, maxDepth)
        subroot.children.append(newNode)
        subroot.point = max(subroot.point, newNode.point)
    random.shuffle(subroot.children)
    subroot.children.sort(reverse=True, key=lambda e: e.point)
    subroot.children = subroot.children[:3]
    return subroot.point


def MinRobot(state, subroot, depth, maxDepth=3):
    if not state.status == 0:
        subroot.point = state.status*10
        return subroot.point
    if depth == maxDepth:
        subroot.point = 0
        return 0
    subroot.point = 999999999999999999
    for freeCell in state.getFreeAdjacentCell():
        newNode = Node(freeCell)
        newNode.point = MaxHuman(state.tickCell(-1,
                                                freeCell), newNode, depth+1, maxDepth)
        subroot.children.append(newNode)
        subroot.point = min(subroot.point, newNode.point)
    subroot.children = [min(subroot.children, key=lambda e: e.point)]
    if subroot.point == 1:
        print(subroot.point)
    return subroot.point


class result:
    def __init__(self, status, node=None, robotCell=None):
        self.status = status
        self.robotCell = robotCell
        self.node = node

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
