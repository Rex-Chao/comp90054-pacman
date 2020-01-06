from captureAgents import CaptureAgent
from game import Directions

import random, time, util, sys
from util import nearestPoint
from game import Actions

def createTeam(firstIndex, secondIndex, isRed,
               first='myAgent', second='myAgent'):
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


class myAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        self.initialPosition = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.allFood = self.getFoodYouAreDefending(gameState).asList()

        self.learningrate = 0.1
        self.discount = 1
        self.eatFoodReward = 1000
        self.eatInvaderReward = -1000
        self.eatCapReward = 1500

        self.weights = util.Counter()
        self.weights['successorScore'] = 50
        self.weights['distance_to_food'] = -1
        self.weights['distance_to_invading_opponent'] = -40
        self.weights['num_invading_opponents'] = -999
        self.weights['distance_to_capsule'] = -10
        self.weights['number_of_capsule'] = 150
        # self.lostFood = []

    #
    def chooseAction(self, gameState):

        state = gameState.getAgentState(self.index)
        legalActs = gameState.getLegalActions(self.index)
        position = state.getPosition()

        opponents = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]

        defendingOpponents = [a for a in opponents if not a.isPacman and a.getPosition() != None]
        distance_to_defendingOpponents = [self.getMazeDistance(position, a.getPosition()) for a in defendingOpponents]

        #找最近的敌人
        closestOpponent = [a for a in defendingOpponents if self.getMazeDistance(position,
                                                                                 a.getPosition()) ==
                           min(distance_to_defendingOpponents)]

        opponents2 = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invadingOpponents = [a for a in opponents2 if a.isPacman and a.getPosition() != None]
        myFood = self.getFoodYouAreDefending(gameState).asList()

        # if (len(self.allFood) - len(myFood) > 0):
        #     self.lostFood = list(set(self.allFood).difference(set(myFood)))

        myTeam = self.getTeam(gameState)

        if (self.index == myTeam[0]):
            brotherPosition = gameState.getAgentState(myTeam[1]).getPosition()
        else:
            brotherPosition = gameState.getAgentState(myTeam[0]).getPosition()

        #如果有敌方入侵
        if len(invadingOpponents) > 0:
            # print("检测到敌人")
            distance_to_invadingOpponent = self.getMazeDistance(position, invadingOpponents[0].getPosition())
            teammate_distance_to_invadingOpponent = self.getMazeDistance(brotherPosition,
                                                                         invadingOpponents[0].getPosition())

            # 正在己方地区的agent去找入侵者麻烦,已经离得太远就算了。。。太远的含义暂定20
            if len(invadingOpponents) > 0 and distance_to_invadingOpponent < 40 and not state.isPacman:
                # 离得比较近的去追
                if distance_to_invadingOpponent <= teammate_distance_to_invadingOpponent:
                        #如果没有被恐惧
                        # print("触发防守")
                        if state.scaredTimer == 0:
                            tmp = 99999
                            for act in legalActs:
                                successor = self.getSuccessor(gameState, act)
                                nextPosition = successor.getAgentPosition(self.index)
                                nextDistance = self.getMazeDistance(invadingOpponents[0].getPosition(), nextPosition)
                                if nextDistance < tmp:
                                    nextAct = act
                                    tmp = nextDistance
                            return nextAct

                        #在被恐惧的情况下定一个安全距离。。。暂定为4
                        elif self.getMazeDistance(position, invadingOpponents[0].getPosition()) >= 4:
                            tmp = 99999
                            for act in legalActs:
                                successor = self.getSuccessor(gameState, act)
                                nextPosition = successor.getAgentPosition(self.index)
                                nextDistance = self.getMazeDistance(invadingOpponents[0].getPosition(), nextPosition)
                                if nextDistance < tmp:
                                    nextAct = act
                                    tmp = nextDistance
                            return nextAct

                        #被恐惧且距离非常近。。跑
                        else:
                            # print("我被恐惧了，距离敌人很近")
                            tmp = 0
                            for act in legalActs:
                                successor = self.getSuccessor(gameState, act)
                                nextPosition = successor.getAgentPosition(self.index)
                                nextDistance = self.getMazeDistance(invadingOpponents[0].getPosition(), nextPosition)
                                if nextDistance > tmp:
                                    nextAct = act
                                    tmp = nextDistance
                            return nextAct

        #不同的设置
        if self.index == myTeam[0]:
            diff = 4
        else:
            diff = 3

        if (len(defendingOpponents) > 0 and not closestOpponent[0].isPacman and not state.isPacman and
                self.getMazeDistance(
                closestOpponent[0].getPosition(), position) <= diff and closestOpponent[0].scaredTimer <= 1):
            # print("看我看我看我")

            acts = [a for a in legalActs if not self.getSuccessor(gameState, a).getAgentState(self.index).isPacman
                   and self.getMazeDistance(position, self.getSuccessor(gameState, a).getAgentState(
                self.index).getPosition()) == 1]
            myTeam = self.getTeam(gameState)
            tmp = 0

            if (self.index == myTeam[0]):
                # print("我是1号，我想远离队友")
                nextAct = []
                for act in acts:
                    successor = self.getSuccessor(gameState, act)
                    nextPosition = successor.getAgentPosition(self.index)
                    next_distance_to_mate = self.getMazeDistance(successor.getAgentState(myTeam[1]).getPosition(),
                                                                 nextPosition)
                    if next_distance_to_mate >= tmp:
                        if next_distance_to_mate == tmp:
                            nextAct.append(act)
                            tmp = next_distance_to_mate
                        else:
                            nextAct = [act]
                            tmp = next_distance_to_mate
                return random.choice(nextAct)
            else:
                # print("我是2号，我想远离队友")
                nextAct = []
                for act in acts:
                    successor = self.getSuccessor(gameState, act)
                    nextPosition = successor.getAgentPosition(self.index)
                    next_distance_to_mate = self.getMazeDistance(successor.getAgentState(myTeam[0]).getPosition(),
                                                                 nextPosition)
                    if next_distance_to_mate >= tmp:
                        if next_distance_to_mate == tmp:
                            nextAct.append(act)
                            tmp = next_distance_to_mate
                        else:
                            nextAct = [act]
                            tmp = next_distance_to_mate
                return random.choice(nextAct)
            return random.choice(nextAct)

        remaining_food = len(self.getFood(gameState).asList())



        #对面有人很靠近时
        if len(defendingOpponents) > 0 and self.getMazeDistance(closestOpponent[0].getPosition(), position) <= 4:
            acts_greedySearch = self.greedySearch(gameState, closestOpponent[0].getPosition())

            if (len(acts_greedySearch) > 0):
                if (acts_greedySearch == 'random' and self.getMazeDistance(closestOpponent[0].getPosition(), position) <= 4):
                    act = [a for a in legalActs if a != 'West' and a != 'East']
                    return random.choice(act)
                else:
                    return acts_greedySearch[0]
            else:
                tmp= 0
                for act in legalActs:
                    successor = self.getSuccessor(gameState, act)
                    nextPosition = successor.getAgentPosition(self.index)
                    next_distance_to_opponent = self.getMazeDistance(closestOpponent[0].getPosition(), nextPosition)
                    if next_distance_to_opponent > tmp:
                        nextAct = act
                        tmp = next_distance_to_opponent
                return nextAct

        # 当对方有防守者的时候
        if (len(defendingOpponents) > 0 and closestOpponent[0].scaredTimer <= 0):
            #此处需确定一个参数，当身上食物数量达到多少时，再浪就不合适了，暂定18。。。
            if state.numCarrying >= 18:
                tmp = 98765
                for act in legalActs:
                    successor = self.getSuccessor(gameState, act)
                    nextPosition = successor.getAgentPosition(self.index)
                    next_distance_to_start = self.getMazeDistance(self.initialPosition, nextPosition)
                    if next_distance_to_start < tmp:
                        nextAct = act
                        tmp = next_distance_to_start
                return nextAct

        #处理进攻端
        values = [self.evaluate(gameState, a) for a in legalActs ]
        maxValue = max(values)
        bestActions = [a for a, v in zip(legalActs, values) if v == maxValue]

        remaining_food = len(self.getFood(gameState).asList())
        # score = gameState.getScore()

        #可获取的食物数量 <=2 或比赛步数所剩不多时(暂定100)，在对面的往己方半场跑，在自己家的执行防守策略
        if remaining_food <= 2 or ((gameState.data.timeleft) <= 100):
            if state.isPacman:
                tmp = 9999
                for act in legalActs:
                    successor = self.getSuccessor(gameState, act)
                    position_now = successor.getAgentPosition(self.index)
                    distance = self.getMazeDistance(self.initialPosition, position_now)
                    if distance < tmp:
                        nextAction = act
                        tmp = distance
                return nextAction

            if not state.isPacman:
                return random.choice(gameState.getLegalActions(self.index))

        return random.choice(bestActions)


    def getFeatures(self, gameState, action):

        features = util.Counter()

        successor = self.getSuccessor(gameState, action)
        remaining_foods = self.getFood(successor).asList()
        features['successorScore'] = -len(remaining_foods)
        capsule_position = self.getCapsules(successor)
        features['number_of_capsule'] = -len(capsule_position)

        features['distance_to_capsule'] = 9999 * len(capsule_position)

        state = successor.getAgentState(self.index)

        position = state.getPosition()

        opponents = [successor.getAgentState(opp) for opp in self.getOpponents(successor)]


        distance_to_capsules = [self.getMazeDistance(position, cp) for cp in capsule_position]
        

        #if (len(distance_to_capsules) > 0):
        closest_capsule = [cap for cap in capsule_position
                               if self.getMazeDistance(position, cap) == min(distance_to_capsules)]

        #
        if (len(closest_capsule) > 0):
            if self.getMazeDistance(position, closest_capsule[0]) <= 4:
                features['distance_to_capsule'] = 9999 * (len(closest_capsule) - 1) \
                                            + self.getMazeDistance(position, closest_capsule[0])

        invadingOpponents = [opp for opp in opponents if opp.isPacman and opp.getPosition() != None]

        if (not state.isPacman):
                features['num_invading_opponents'] = len(invadingOpponents)
                distance_to_invading_opponents = [self.getMazeDistance(position, a.getPosition()) for a in
                                                  invadingOpponents]
                closest_invading_opponent = [a for a in invadingOpponents
                                             if self.getMazeDistance(position, a.getPosition())
                                             == min(distance_to_invading_opponents)]
                #if (len(invadingOpponents) > 0):
                if (len(closest_invading_opponent) > 0 and self.getMazeDistance(position, closest_invading_opponent[
                        0].getPosition())) < 13:
                    if (len(invadingOpponents) > 0):
                        distance_to_invading_opponents = [self.getMazeDistance(position, a.getPosition()) for a in
                                                      invadingOpponents]
                        features['distance_to_invading_opponent'] = min(distance_to_invading_opponents)
                        features['num_invading_opponents'] = len(invadingOpponents)
                        # print("情况11111")
                        return features

        features['distance_to_food'] = 9999

        if len(remaining_foods) > 0:
            myPos = successor.getAgentState(self.index).getPosition()
            teamIndex = self.getTeam(successor)
            foodMin = []

            yFoodMax = 0
            yFoodMin = 50
            foodL = []
            foodH = []
            for food in remaining_foods:
                if (food[1] >= yFoodMax):
                    if (food[1] == yFoodMax):
                        foodH.append(food)
                    else:
                        foodH = []
                        yFoodMax = food[1]
                        foodH.append(food)
                if food[1] <= yFoodMin:
                    if food[1] == yFoodMin:
                        foodL.append(food)
                    else:
                        foodL = []
                        yFoodMin = food[1]
                        foodL.append(food)

            minn = foodL[0][0]
            minF = foodL[0]
            maxx = foodH[0][0]
            maxF = foodH[0]
            for food in foodL:
                if food[0] < minn:
                    minn = food[0]
                    minF = food
            for food in foodH:
                if food[0] < maxx:
                    maxx = food[0]
                    maxF = food
            if not state.isPacman:
                minD = 99999
                for food in remaining_foods:
                    distance = self.getMazeDistance(myPos, food)
                    if (distance < minD):
                        secondD = minD
                        minD = distance
                    elif distance > minD and distance < secondD:
                        secondD = distance
                if (minD >= 10):
                    if (len(foodL) != 0):
                        if (self.index == teamIndex[0]):
                            distance = self.getMazeDistance(myPos, minF)
                            features['distance_to_food'] = distance
                            return features
                    if (len(foodH) != 0):
                        if self.index == teamIndex[1]:
                            distance = self.getMazeDistance(myPos, maxF)
                            features['distance_to_food'] = distance

                            return features
                else:
                    features['distance_to_food'] = minD
            if (self.index == teamIndex[0]):
                teammatePos = successor.getAgentState(teamIndex[1]).getPosition()
                minD = 99999
                for food in remaining_foods:
                    distance = self.getMazeDistance(myPos, food)
                    if (distance < minD):
                        secondD = minD
                        minD = distance
                    elif distance > minD and distance < secondD:
                        secondD = distance
                food = [food for food in remaining_foods if self.getMazeDistance(myPos, food) == minD]
                minDistanceToTeammate = self.getMazeDistance(teammatePos, food[0])
                if (minD >= minDistanceToTeammate):
                    features['distance_to_food'] = secondD
                    return features
                else:
                    features['distance_to_food'] = minD
                    return features

            if (self.index == teamIndex[1]):
                teammatePos = successor.getAgentState(teamIndex[0]).getPosition()
                minD = 99999
                for food in remaining_foods:
                    distance = self.getMazeDistance(myPos, food)
                    if (distance <= minD):
                        if (distance == minD):
                            foodMin.append(food)
                        else:
                            secondD = minD
                            minD = distance
                            foodMin = []
                            foodMin.append(food)
                    elif distance > minD and distance < secondD:
                        secondD = distance

                food = [food for food in remaining_foods if self.getMazeDistance(myPos, food) == minD]
                minDistanceToTeammate = self.getMazeDistance(teammatePos, food[0])

                if (minD > minDistanceToTeammate):
                    features['distance_to_food'] = secondD
                    return features
                else:
                    features['distance_to_food'] = minD
                    return features
        # print("情况888888")
        return features

    #
    def getWeights(self, gameState, action):
        return {'successorScore': 50, 'distance_to_food': -1,
                'distance_to_invading_opponent': -40, 'num_invading_opponents': -999,
               'distance_to_capsule': -10, 'number_of_capsule': 150
                }


    def manhattanDistance(self,position1, position2):  # calculate manhattan distance of two given points
        xy1 = list(position1)
        xy2 = list(position2)
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor


    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights


    def isGoalState(self, state):

        if state.getAgentState(self.index).isPacman:
            return False
        else:
            return True


    def runHeuristic(self,state,opponent_position):

        position = state.getAgentState(self.index).getPosition()
        return -2*self.getMazeDistance(position, opponent_position)+self.getMazeDistance(position, self.initialPosition)


    ######贪婪最佳优先搜索
    def greedySearch(self, gameState, enemyPos):

        from util import PriorityQueue

        pQueue = PriorityQueue()
        visited_Node = []
        directions = []
        cost = 0
        preCost = 0
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        pQueue.push((gameState, directions, cost, preCost, myPos), cost)
        while not pQueue.isEmpty():

            c_node_state = pQueue.pop()

            if self.isGoalState(c_node_state[0]):
                if (len(c_node_state[1]) == 0):
                    return 'random'
                else:
                    return c_node_state[1]
            if c_node_state[4] in visited_Node:
                continue
            else:
                visited_Node.append(c_node_state[4])
                gameState1 = c_node_state[0]
                actions = gameState1.getLegalActions(self.index)

                for a in actions:
                    new_direction = list(c_node_state[1])
                    new_direction.append(a)
                    new_cost = self.runHeuristic(gameState1, enemyPos)

                    myStateNow = gameState1.getAgentState(self.index)
                    myPosNow = myStateNow.getPosition()
                    nmyState = self.getSuccessor(gameState1, a).getAgentState(self.index)
                    nmyPos = nmyState.getPosition()

                    if self.getMazeDistance(nmyPos, myPosNow) == 1:

                        if self.getMazeDistance(enemyPos, nmyPos) == 1 and len(list(new_direction)) == 1:
                            continue

                        elif len(c_node_state[1]) < 15:
                            pCost = len(c_node_state[1]) * 1.8
                            pQueue.push(
                                (self.getSuccessor(gameState1, a), new_direction, new_cost + pCost, pCost, nmyPos),
                                new_cost + pCost)
                        else:
                            pCost = len(c_node_state[1]) * len(c_node_state[1]) / 5
                            pQueue.push(
                                (self.getSuccessor(gameState1, a), new_direction, new_cost + pCost, pCost, nmyPos),
                                new_cost + pCost)

        return directions


    def gettingRewards(self, gameState, action):
        succGameState = self.getSuccessor(gameState, action)
        currEnemies = [gameState.getAgentState(i)
                       for i in self.getOpponents(gameState)]
        succEnemies = [succGameState.getAgentState(i)
                       for i in self.getOpponents(succGameState)]

        # rewards for getting food
        food_now = self.getFood(gameState).asList()
        food_after = self.getFood(succGameState).asList()
        if len(food_now) - len(food_after) == 1:
            return self.eatFoodReward

        # rewards for defending opponents
        invading_opponents_now= [enemy for enemy in currEnemies
                                 if enemy.isPacman and enemy.getPosition() != None]
        invading_opponents_after = [enemy for enemy in succEnemies
                                    if enemy.isPacman and enemy.getPosition() != None]
        if len(invading_opponents_now) - len(invading_opponents_after) == 1:
            return self.eatInvaderReward

        # rewards for getting capsules
        capules_now = self.getCapsules(gameState)
        capules_after = self.getCapsules(succGameState)
        if len(capules_now) - len(capules_after) == 1:
            return self.eatCapReward

        return 0


    def computeNextValueFromQValues(self, gameState):
            legalActions = gameState.getLegalActions(self.index)
            if len(legalActions) == 0:
                return 0.0
            else:
                tmpValue = None
                for action in legalActions:
                    gameState_after = self.getSuccessor(gameState, action)
                    legalActions_after = \
                        gameState_after.getLegalActions(self.index)
                    value_after = max([self.evaluate(gameState_after, a)
                                       for a in legalActions_after])
                    if value_after > tmpValue:
                        tmpValue = value_after
                return tmpValue


    def updateWeights(self, gameState, action):
            features = self.getFeatures(gameState, action)
            tmpWeights = self.weights.copy()
            for feature in features:
                difference = self.gettingRewards(gameState, action) + \
                             (self.discount *
                              self.computeNextValueFromQValues(gameState)) \
                             - self.evaluate(gameState, action)
                tmpWeights[feature] += self.learningrate *\
                                       difference * features[feature]
            return tmpWeights





