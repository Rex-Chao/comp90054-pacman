# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
import math

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from game import Actions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DefensiveAgent', second = 'OffensiveAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class OffensiveAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        """
        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)
        self.birthPosition = gameState.getAgentPosition(self.index)
        '''
        Your initialization code goes here, if you need any.
        '''


    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)
        position = gameState.getAgentPosition(self.index)

        # print(gameState.getAgentState(self.index).numCarrying)
        enemys = self.getOpponents(gameState)
        if gameState.getAgentPosition(self.index) != self.birthPosition:
            if gameState.getAgentState(self.index).isPacman:
                path = uct_for_pacman(gameState, self)
                if not path == "UCT_Fail":
                    print("此步来自uct搜索树")
                    return path

        if not gameState.getAgentState(self.index).isPacman:
            for enemy_index in enemys:
                if gameState.getAgentState(enemy_index).isPacman:
                    enemy_position = gameState.getAgentPosition(enemy_index)
                    # print(enemy_position)
                    if enemy_position is not None:
                        path = aStarFindPath_defence(gameState, enemy_position, self)
                        if path != "A*fail":
                            return path

        foodCarrying = gameState.getAgentState(self.index).numCarrying

        if (foodCarrying > 3) or (self.getFood(gameState).count() <= 2):
            path_firstAction = aStarFindPath(gameState, position, self.birthPosition, self)
        else:
            foodList = self.getFood(gameState).asList()

            distance_closestFood = 1000000
            position_closestFood = None


            for food in foodList:
                distance = self.getMazeDistance(position, food)
                if distance < distance_closestFood:
                    distance_closestFood = distance
                    position_closestFood = food

            path_firstAction = aStarFindPath(gameState, position, position_closestFood, self)
            if path_firstAction == "A*Block":
                path_firstAction = aStarFindPath(gameState, position, self.birthPosition, self)
            # path_firstAction = aStarFindPath(gameState, position, position_farFood, self)
            # print(path)
            #
            # print(gameState.getAgentPosition(self.index))
            # print(gameState.getAgentDistances())

        if path_firstAction == "A*Block":
            print("没办法呀")
            return random.choice(actions)
        else:
            return path_firstAction
        # return random.choice(actions)


class DefensiveAgent(CaptureAgent):

  def registerInitialState(self, gameState):
    """
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)
    IMPORTANT: This method may run for at most 15 seconds.
    """
    CaptureAgent.registerInitialState(self, gameState)
    self.birthPosition = gameState.getAgentPosition(self.index)
    self.up = True


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    enemys = self.getOpponents(gameState)
    for enemy_index in enemys:
        if gameState.getAgentState(enemy_index).isPacman:
            enemy_position = gameState.getAgentPosition(enemy_index)
            # print(enemy_position)
            if enemy_position is not None:
                path = aStarFindPath_defence(gameState, enemy_position, self)
                if path != "A*fail":
                    return path

    map_game_hight = self.getFood(gameState).height
    map_game_width = self.getFood(gameState).width
    upper = map_game_hight-6    #最上面一行能走的是map_game_hight-2
    lower = 4                   #最下面一行能走的是1
    if self.red:
        middleLine = map_game_width/2-1
    else:
        middleLine = map_game_width/2

    if self.up:
        path = aStarFindPath_defence(gameState, (middleLine, upper), self)
        if path == "A*fail":
            self.up = False
            path = aStarFindPath_defence(gameState, (middleLine, lower), self)
    else:
        path = aStarFindPath_defence(gameState, (middleLine, lower), self)
        if path == "A*fail":
            self.up = True
            path = aStarFindPath_defence(gameState, (middleLine, upper), self)

    if path == "A*fail":
        return random.choice(actions)
    else:
        return path


def aStarFindPath(gameState, startPosition, goalPosition, agent):
    open_list = util.PriorityQueue()
    # (position, action, cost), g(s), self, pre
    open_list.push(((startPosition, 'initial', 0), 0, 1, 0),
                   0 + heuristicForAStar(gameState, startPosition, agent, startPosition))
    # print("我就想知道初始位置的h值是："+str(heuristicForAStar(gameState, startPosition, agent, startPosition)))
    count = 2
    best_g = {startPosition: 0}
    close_list = []
    visited = [startPosition]

    while not open_list.isEmpty():
        node = open_list.pop()
        if (node not in close_list) or (node[1] < best_g[node[0][0]]):
            if node not in close_list:
                close_list.append(node)
            best_g[node[0][0]] = node[1]
            if node[0][0] == goalPosition:
                list_reverse = util.Stack()
                list_reverse.push(node[0][1])
                while node[2] > 1:
                    list_reverse.push(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                # list_return = []
                # while not list_reverse.isEmpty():
                #     list_return.append(list_reverse.pop())
                # return list_return
                return list_reverse.pop()

            successors = []
            legalPositions = [p for p in gameState.getWalls().asList(False)]
            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                x, y = node[0][0]
                dx, dy = Actions.directionToVector(direction)
                nextx, nexty = int(x + dx), int(y + dy)
                if (nextx, nexty) in legalPositions:
                    successors.append(((nextx, nexty), direction, 1))

            for successor in successors:
                if (successor[0] not in visited) and \
                        heuristicForAStar(gameState, startPosition, agent, successor[0]) == 1:
                    open_list.push((successor, node[1] + 1, count, node[2]),
                                   node[1] + 1 + heuristicForAStar(gameState, startPosition, agent, successor[0]))
                    count += 1
                    visited.append(successor[0])
    return "A*Block"


def heuristicForAStar(gameState, selfPostion, agent, evaluate_position):
    # print("被evalue的坐标是"+ str(evaluate_position))
    enemys = agent.getOpponents(gameState)
    distance_me = agent.getMazeDistance(selfPostion, evaluate_position)
    distance_enemy = 0
    enemy_flag = 0
    for enemy_index in enemys:
        if not gameState.getAgentState(enemy_index).isPacman:
            if gameState.getAgentState(enemy_index).scaredTimer == 0:
                enemy_position = gameState.getAgentPosition(enemy_index)
                # print(enemy_position)
                if enemy_position is not None:
                    enemy_flag += 1
                    distance_enemy += agent.getMazeDistance(enemy_position, evaluate_position)
                    # print("我方距离是"+str(distance_me))
                    # print("敌方距离是" + str(distance_enemy))
    if enemy_flag == 0:
        return 1
    else:
        if distance_enemy <= distance_me:
            return 1000
        else:
            return 1


def aStarFindPath_defence(gameState, goalPosition, agent):
    if gameState.getAgentPosition(agent.index) == goalPosition:
        return "A*fail"
    open_list = util.PriorityQueue()
    position_start = gameState.getAgentPosition(agent.index)
    # (position, action, cost), g(s), self, pre
    open_list.push(((position_start, 'initial', 0), 0, 1, 0),
                   0 + 1)
    count = 2
    best_g = {position_start: 0}
    close_list = []
    visited = [position_start]

    while not open_list.isEmpty():
        node = open_list.pop()
        # (position, action, cost), g(s), self, pre
        #    [0][0]   [0][1]  [0][2]  [1]   [2]  [3]
        if (node not in close_list) or (node[1] < best_g[node[0][0]]):
            if node not in close_list:
                close_list.append(node)
            best_g[node[0][0]] = node[1]
            if node[0][0] == goalPosition:
                list_reverse = util.Stack()
                list_reverse.push(node[0][1])
                while node[2] > 1:
                    list_reverse.push(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return list_reverse.pop()

            successors = []
            legalPositions = [p for p in gameState.getWalls().asList(False)]
            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                x, y = node[0][0]
                dx, dy = Actions.directionToVector(direction)
                nextx, nexty = int(x + dx), int(y + dy)
                if (nextx, nexty) in legalPositions:
                    if (agent.red and nextx <= goalPosition[0]) or ((not agent.red) and nextx >= goalPosition[0]):
                        successors.append(((nextx, nexty), direction, 1))

            for successor in successors:
                if successor[0] not in visited:
                    open_list.push((successor, node[1] + 1, count, node[2]),
                                   node[1] + 1 + 1)
                    count += 1
                    visited.append(successor[0])
    return "A*fail"


'''
def searchTreeForPacman(gameState, agent):
    print("开始进入搜索树")
    position_me = gameState.getAgentPosition(agent.index)
    legalPositions = [p for p in gameState.getWalls().asList(False)]
    mapFood = agent.getFood(gameState)
    foodCarring = gameState.getAgentState(agent.index).numCarrying
    enemyList_index = agent.getOpponents(gameState)
    enemyList_position = []
    for enemy_index in enemyList_index:
        enemy_position = gameState.getAgentPosition(enemy_index)
        if enemy_position is not None:
            enemyList_position.append(enemy_position)
    tree = generateSearchTreeNode("initial", legalPositions, mapFood, position_me, enemyList_position, foodCarring, 2)
    print("子节点的数据量")
    print(len(tree.childrenNode))
    rootKeys = tree.childrenNode.keys()
    print(rootKeys)
    maxFoodCarring = 0
    bestAction = None
    for action in rootKeys:
        if tree.childrenNode[action].foodCarring > maxFoodCarring:
            maxFoodCarring = tree.childrenNode[action].foodCarring
            bestAction = action
    if bestAction is None:
        print("搜索树出问题啦")
        return "SearchTreeFail"
    else:
        return bestAction


def generateSearchTreeNode(action, legalPositions, mapFood, position_me, positionList_enemy, carringFood, limit):
    print("开始第"+str(limit)+"层迭代")
    if position_me in positionList_enemy:
        return None
    node = SearchTreeNode(action, position_me, positionList_enemy, carringFood)
    if limit == 0:
        return node
    else:
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST, Directions.STOP]:
            x, y = position_me
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if (nextx, nexty) in legalPositions:
                carringFood_new = carringFood
                mapFood_new = mapFood.copy()
                positionList_enemy_new = []
                for enemyPosition in positionList_enemy:
                    action_enemy = aStarFindPath_all(legalPositions, enemyPosition, position_me)
                    dx2, dy2 = Actions.directionToVector(action_enemy)
                    nextx2, nexty2 = int(enemyPosition[0] + dx2), int(enemyPosition[1] + dy2)
                    positionList_enemy_new.append((nextx2, nexty2))

                if mapFood[nextx][nexty]:
                    carringFood_new += 1
                    mapFood_new[nextx][nexty] = False
                node.childrenNode.append(
                    generateSearchTreeNode(direction, legalPositions, mapFood_new, (nextx,nexty),
                                           positionList_enemy_new, carringFood_new, limit-1))
'''


def uct_for_pacman(gameState, agent):
    print("开始进入uct搜索树")
    position_me = gameState.getAgentPosition(agent.index)
    legalPositions = [p for p in gameState.getWalls().asList(False)]
    foodGrid = agent.getFood(gameState)
    foodCarrying = gameState.getAgentState(agent.index).numCarrying
    enemyList_index = agent.getOpponents(gameState)
    enemyList_position = []
    for enemy_index in enemyList_index:
        enemy_position = gameState.getAgentPosition(enemy_index)
        if enemy_position is not None:
            enemyList_position.append(enemy_position)

    root = SearchTreeNode('Root', position_me, enemyList_position, foodCarrying, None, legalPositions, foodGrid)
    limit = 5
    i = 0
    while i < limit:
        leaf = uct_select(root)
        node_withChildren = uct_expand(leaf)
        child = uct_select(node_withChildren)
        child = uct_simulate(child)
        root = uct_backup(child)
        print("现在是第" + str(i+1) + "次迭代uct")
        # for child in root.children:
        #     print(child.action + " : " + str(child.q_value) + " : " + str(child.visit) + " : " + str(child.position_me))
        print_uct_tree(root, 0)
        i += 1

    if len(root.children) == 0:
        print("卧槽uct说无路可走！")
        return "UCT_Fail"
    else:
        best_child = root.children[0]
        for child in root.children:
            # print(child.action+" : "+str(child.q_value)+" : "+str(child.visit)+" : "+str(child.position_me))
            if child.q_value > best_child.q_value:
                best_child = child
        return best_child.action



def aStarFindPath_all(legalPositions, startPosition, goalPosition):
    if startPosition == goalPosition:
        return "Stop"
    open_list = util.PriorityQueue()
    # (position, action, cost), g(s), self, pre
    open_list.push(((startPosition, 'initial', 0), 0, 1, 0),
                   0 + 1)
    count = 2
    best_g = {startPosition: 0}
    close_list = []
    visited = [startPosition]

    while not open_list.isEmpty():
        node = open_list.pop()
        # (position, action, cost), g(s), self, pre
        #    [0][0]   [0][1]  [0][2]  [1]   [2]  [3]
        if (node not in close_list) or (node[1] < best_g[node[0][0]]):
            if node not in close_list:
                close_list.append(node)
            best_g[node[0][0]] = node[1]
            if node[0][0] == goalPosition:
                list_reverse = util.Stack()
                list_reverse.push(node[0][1])
                while node[2] > 1:
                    list_reverse.push(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return list_reverse.pop()

            successors = []
            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                x, y = node[0][0]
                dx, dy = Actions.directionToVector(direction)
                nextx, nexty = int(x + dx), int(y + dy)
                if (nextx, nexty) in legalPositions:
                    successors.append(((nextx, nexty), direction, 1))

            for successor in successors:
                if successor[0] not in visited:
                    open_list.push((successor, node[1] + 1, count, node[2]),
                                   node[1] + 1 + 1)
                    count += 1
                    visited.append(successor[0])
    return "A*fail"

class SearchTreeNode:
    def __init__(self, action, position_me, positions_enemys, foodCarrying, parentNode, legalPositions, foodGrid):
        self.action = action
        self.position_me = position_me
        self.foodCarrying = foodCarrying
        self.enemyList_position = positions_enemys
        self.parent = parentNode
        self.foodGrid = foodGrid
        self.legalPositions = legalPositions
        self.children = []
        self.q_value = -2000
        self.visit = 0


# UCT select step
def uct_select(node):
    if len(node.children) == 0:
        return node
    else:
        # child_best = node.children[0]
        # ucb_best = node.children[0].q_value + ucb_right(node.visit, child_best.visit)
        # for child in node.children:
        #     if child.q_value + ucb_right(node.visit, child.visit) > ucb_best:
        #         ucb_best = child.q_value + ucb_right(node.visit, child.visit)
        #         child_best = child
        # return child_best
        return uct_select(random.choice(node.children))

def ucb_right(parentVisit, childVisit):
    if childVisit == 0:
        return 10000
    else:
        return 8 * math.sqrt(2.0 * math.log(parentVisit) / childVisit)


# UCT expand step
def uct_expand(node):
    for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
        x, y = node.position_me
        dx, dy = Actions.directionToVector(direction)
        nextx, nexty = int(x + dx), int(y + dy)
        if (nextx, nexty) in node.legalPositions:
            enemyList_position_new = []
            if len(node.enemyList_position) == 0:
                enemyList_position_new = []
            else:
                for enemy_position in node.enemyList_position:
                    path_enemy = aStarFindPath_all(node.legalPositions, enemy_position, node.position_me)
                    dx2, dy2 = Actions.directionToVector(path_enemy)
                    nextx2, nexty2 = int(enemy_position[0] + dx2), int(enemy_position[1] + dy2)
                    enemyList_position_new.append((nextx2, nexty2))
            if node.foodGrid[nextx][nexty]:
                foodCarrying_new = node.foodCarrying + 1
                foodGrid_new = node.foodGrid.copy()
                foodGrid_new[nextx][nexty] = False
            else:
                foodCarrying_new = node.foodCarrying
                foodGrid_new = node.foodGrid.copy()
            node_new = SearchTreeNode(direction, (nextx, nexty), enemyList_position_new,
                                      foodCarrying_new, node, node.legalPositions, foodGrid_new)
            if not uct_check_already_in_tree(findRootNodeOfTree(node), node_new):
                node.children.append(node_new)
    return node


def uct_check_already_in_tree(node, node_new):
    if node is node_new:
        return True
    if len(node.children) == 0:
        return False
    for child in node.children:
        if uct_check_already_in_tree(child, node_new):
            return True
    return False


def findRootNodeOfTree(node):
    if node.parent is None:
        return node
    else:
        return findRootNodeOfTree(node.parent)


# UCT simulate step
def uct_simulate(node):
    q_value = 0
    if node.position_me in node.enemyList_position:
        q_value -= 1000
    q_value += node.foodCarrying * 100
    node.q_value = q_value
    return node


# UCT backup step
def uct_backup(node):
    node.visit += 1
    if node.parent is None:
        return node
    else:
        parentNode = node.parent
        value_calculation = 0 + 0.1 * node.q_value  #week8-1-P16
        if parentNode.q_value < value_calculation:
            parentNode.q_value = value_calculation
        return uct_backup(parentNode)


def print_uct_tree(root, layer):
    i = layer*4
    while i > 0:
        print(" ", end=" ")
        i -= 1
    print(root.action, root.position_me, root.visit, root.q_value)
    for child in root.children:
        print_uct_tree(child, layer+1)










