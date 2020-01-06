
import sys
sys.path.append('teams/WhatsUrProblem/')

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
               first='DefensiveAgent', second='OffensiveAgent'):

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
        self.isOffender = True
        self.enemyList_index = self.getOpponents(gameState)
        gameMap = gameState.getWalls()
        if self.red:
            self.middleLine_me = int(gameMap.width / 2 - 1)
            self.middleLine_enemy = int(gameMap.width / 2)
        else:
            self.middleLine_me = int(gameMap.width / 2)
            self.middleLine_enemy = int(gameMap.width / 2 - 1)
        self.repeat_count = 0
        self.action_last_turn = 'Stop'

        index_teamMembers = self.getTeam(gameState)
        if self.index == index_teamMembers[0]:
            self.index_teammate = index_teamMembers[1]
        else:
            self.index_teammate = index_teamMembers[0]

        self.home_positionList = []
        legalPositions = [p for p in gameState.getWalls().asList(False)]
        for p in legalPositions:
            if p[0] == self.middleLine_me:
                self.home_positionList.append(p)
        self.enemyPosition_lastTime = None
        self.enemyIndex_lastTime = None
        self.die_count = 0

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        # return keep_advantage_offender(gameState, self)

        # print("进攻方行动")
        actions = gameState.getLegalActions(self.index)
        self.capsule_time = 0
        self.food_time = 0
        self.escape_time = 0
        self.capsule_position_for_time = 0
        self.turn_left = int(gameState.data.timeleft / 4)

        if not gameState.getAgentState(self.index).isPacman:
            self.die_count = 0

        if self.getFood(gameState).count() <= 2:
            # 目前剩余食物数小于2，只要回到大本营就赢了
            path_escape = aStarFindPath_forPacman_withAvoid \
                (gameState, find_best_escape_point_using_position \
                    (self, gameState, gameState.getAgentPosition(self.index)), self)
            if path_escape != "A*Fail":
                if path_escape == 'Stop':
                    # 这个地方其实表示吃够豆子游戏结束，所以如无必要不必加横跳判断
                    return 'Stop'
                else:
                    action_choose = path_escape.pop()
                    # print("吃剩两个食物时，进攻方在回城路上:"+action_choose)
                    # return action_choose
            else:
                # 找不到回城的路，建议执行二阶攻方策略
                action_choose = level_2_offence(gameState, self)
                if action_choose not in actions:
                    print("进攻方决定采取非法动作")
                    return random.choice(actions)
                # return action_choose

            # 把原本的分别return放在最下面，便于统计横跳计数
            action_choose = repeat_detection_for_offender(self, action_choose)
            # print("此步来自食物数小于2的策略")
            return action_choose

        enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, self)
        if len(enemyList_position) > 0:
            # 进攻方可以探测到敌人坐标，但也许是防守方发现的
            # 执行二阶进攻策略
            # 目前采取激进二阶策略，只考虑进攻方视野内的敌人
            action_choose = level_2_offence(gameState, self)
            if action_choose not in actions:
                print("进攻方决定采取非法动作")
                return random.choice(actions)
            # 此处统计横跳计数
            action_choose = repeat_detection_for_offender(self, action_choose)
            return action_choose

        # 到这说明地图上看不到敌人
        # 执行一阶进攻策略
        action_choose = level_1_offence(gameState, self)
        if action_choose not in actions:
            print("进攻方决定采取非法动作")
            return random.choice(actions)
        # 此处统计横跳计数
        action_choose = repeat_detection_for_offender(self, action_choose)
        return action_choose


class DefensiveAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        """
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)
    IMPORTANT: This method may run for at most 15 seconds.
    """
        CaptureAgent.registerInitialState(self, gameState)
        self.isOffender = False
        self.foodGrid_defence_lastTime = self.getFoodYouAreDefending(gameState)
        self.enemyPosition_lastTime = None
        self.enemyList_index = self.getOpponents(gameState)
        self.attackerList_position = []
        self.legalPositions = [p for p in gameState.getWalls().asList(False)]

        gameMap = gameState.getWalls()
        if self.red:
            self.middleLine_me = int(gameMap.width / 2 - 1)
            self.middleLine_enemy = int(gameMap.width / 2)
        else:
            self.middleLine_me = int(gameMap.width / 2)
            self.middleLine_enemy = int(gameMap.width / 2 - 1)
        self.middleHeight = int(gameMap.height / 2)

        index_teamMembers = self.getTeam(gameState)
        if self.index == index_teamMembers[0]:
            self.index_teammate = index_teamMembers[1]
        else:
            self.index_teammate = index_teamMembers[0]

        self.home_positionList = []
        legalPositions = [p for p in gameState.getWalls().asList(False)]
        for p in legalPositions:
            if p[0] == self.middleLine_me:
                self.home_positionList.append(p)
        self.enemyPosition_lastTime = None
        self.enemyIndex_lastTime = None
        self.die_count = 0

    # choose action for defender
    def chooseAction(self, gameState):
        # print("防守方行动")
        actions = gameState.getLegalActions(self.index)
        # 这些参数只用于进攻方，但由于防守方使用了进攻方的某些方法，为了省事没有仔细筛选直接拷过来了
        self.capsule_time = 0
        self.food_time = 0
        self.escape_time = 0
        self.capsule_position_for_time = 0
        self.turn_left = int(gameState.data.timeleft / 4)
        if not gameState.getAgentState(self.index).isPacman:
            self.die_count = 0

        if gameState.getAgentState(self.index).scaredTimer > 0:
            # 处于闪光状态下，执行防守三阶策略
            return level_3_defender(gameState, self)

        if gameState.getAgentState(self.index).isPacman:
            # 当防守方为pacman
            # 根据当前算法，此情况只会发生在因为闪光状态而发生的躲避事件
            # 没什么好说的，想办法回城
            # 事实上，此处执行的是进攻方目标食物数小于2时所采取的策略
            path_escape = aStarFindPath_forPacman_withAvoid \
                (gameState, find_best_escape_point_using_position \
                    (self, gameState, gameState.getAgentPosition(self.index)), self)
            if path_escape != "A*Fail":
                if path_escape == 'Stop':
                    return 'Stop'
                else:
                    action_choose = path_escape.pop()
                    # print("防守方在闪光状态结束且不在本方情况下执行的回城动作："+action_choose)
                    return action_choose
            else:
                # 找不到回城的路，建议执行二阶攻方策略
                action_choose = level_2_offence(gameState, self)
                if action_choose not in actions:
                    print("采取非法动作")
                    return random.choice(actions)
                return action_choose
        else:
            # 防守方正常在家防御
            attacker_flag = False
            attackerList_position = []
            for enemy_index in self.enemyList_index:
                if gameState.getAgentState(enemy_index).isPacman:
                    attacker_flag = True
                    enemy_position = gameState.getAgentPosition(enemy_index)
                    if enemy_position is not None:
                        attackerList_position.append(enemy_position)

            self.attackerList_position = attackerList_position

            if attacker_flag:
                action_choose = level_2_defender(gameState, self)
                if action_choose not in actions:
                    print("防御者决定采取非法动作")
                    return random.choice(actions)
                # print("二阶："+action_choose)
                return action_choose
            else:
                # 自己这边的地盘上没有敌人
                self.enemyPosition_lastTime = None
                action_choose = level_1_defender(gameState, self)
                if action_choose not in actions:
                    print("防御者决定采取非法动作")
                    return random.choice(actions)
                # print("一阶："+action_choose)
                return action_choose
        print("防守方无路可走")
        return random.choice(actions)


def level_1_offence(gameState, agent):
    path_escape = aStarFindPath_forPacman_withAvoid \
        (gameState, find_best_escape_point_using_position \
            (agent, gameState, gameState.getAgentPosition(agent.index)), agent)
    if agent.turn_left < len(path_escape) + 3 and gameState.getAgentState(agent.index).numCarrying > 0:
        # print("身上还有食物，没时间了，必须回城")
        if path_escape != "A*Fail":
            if path_escape == 'Stop':
                # 说明没时间了并且也来不及吃食物了，应该执行攻转防守保胜策略
                # print("没时间了并且也来不及吃食物了，应该执行进攻方保胜策略")
                action_choose = keep_advantage_offender(gameState, agent)
                return action_choose
            else:
                action_choose = path_escape.pop()
                return action_choose
    return value_iteration_offence(gameState, agent)


def level_2_offence(gameState, agent):
    # 目前地图上只要能看到敌人，就执行下面步骤
    # 目前还没发现高阶防守策略的玩家，所以删去所有绝对安全的策略，全部采用风险策略

    # 不能保证绝对安全吃食物的情况下
    food_first_path_in_escape_risk = find_way_to_nearestFood_with_avoid_and_risk(gameState, agent)
    if food_first_path_in_escape_risk[0] != "NoWayToFood" \
            and food_first_path_in_escape_risk[1] != "A*Fail":
        action_with_risk = risk_eat_food_with_enemy(food_first_path_in_escape_risk, gameState, agent)
        if action_with_risk == "SafeNow":
            # print("SafeNow")
            return level_1_offence(gameState, agent)
        if action_with_risk == "NoTime":
            # print("没时间了，必须回城")
            path_escape = aStarFindPath_forPacman_withAvoid \
                (gameState, find_best_escape_point_using_position \
                    (agent, gameState, gameState.getAgentPosition(agent.index)), agent)
            if path_escape != "A*Fail":
                if path_escape == 'Stop':
                    # 说明没时间了并且也来不及吃食物了，应该执行攻转防守保胜策略
                    # print("没时间了并且也来不及吃食物了，应该执行进攻方保胜策略")
                    action_choose = keep_advantage_offender(gameState, agent)
                    return action_choose
                else:
                    # print("没时间了并且也不是stop，继续跑")
                    action_choose = path_escape.pop()
                    # print("二阶进攻时间不足且在回城路上：" + action_choose)
                    return action_choose
        if action_with_risk == "Die":
            # print("二阶进攻判断已死")
            # 修改为返回一阶策略中value_iteration的结果。根据观察对战记录，有的敌人比较瓜，当我判断必死时，实际并非如此。
            # 所以通过一阶值迭代，让它面临必死境地时，总是朝远离敌人的方向跑
            actions = gameState.getLegalActions(agent.index)
            # return random.choice(actions)
            action_choose = level_1_offence(gameState, agent)
            agent.die_count += 1
            if agent.die_count >= 5:
                point_escape_though_die = \
                    find_closest_escape_point_using_position(agent, gameState, gameState.getAgentPosition(agent.index))
                legalPositions_all_map = [p for p in gameState.getWalls().asList(False)]
                action_choose_though_die = \
                    aStarFindPath_all_for_deadcace(legalPositions_all_map,
                                                   gameState.getAgentPosition(agent.index), point_escape_though_die)
                # actions = gameState.getLegalActions(agent.index)
                if action_choose_though_die not in actions:
                    print("送死策略产生非法操作")
                    return random.choice(actions)
                return action_choose_though_die
            else:
                if action_choose not in actions:
                    print("送死策略产生非法操作")
                    return random.choice(actions)
                return action_choose
        else:
            # print("二阶进攻返回值"+action_with_risk)
            return action_with_risk
    else:
        action_choose = find_way_to_nearest_capsule(gameState, agent)
        # print("侦测到危险ghost，开始找吃胶囊的路："+action_choose)
        if action_choose != "NoWayToCapsule":
            return action_choose
        else:
            path_escape = aStarFindPath_forPacman_withAvoid \
                (gameState, find_best_escape_point_using_position \
                    (agent, gameState, gameState.getAgentPosition(agent.index)), agent)
            if path_escape != "A*Fail":
                if path_escape == 'Stop':
                    print("目测已经跑到安全地方了")  # 目前只有这一行代码所以不能注释
                    # return 'Stop'
                else:
                    action_choose = path_escape.pop()
                    return action_choose
    # print("二阶进攻无路可走")
    actions = gameState.getLegalActions(agent.index)
    if not gameState.getAgentState(agent.index).isPacman:
        action_choose = keep_advantage_offender(gameState, agent)
        if action_choose not in actions:
            return random.choice(actions)
        return action_choose

    action_choose = level_1_offence(gameState, agent)
    agent.die_count += 1
    # print("死亡计数器现在是：" + str(agent.die_count))
    if agent.die_count >= 5:
        point_escape_though_die = \
            find_closest_escape_point_using_position(agent, gameState, gameState.getAgentPosition(agent.index))
        legalPositions_all_map = [p for p in gameState.getWalls().asList(False)]
        action_choose_though_die = \
            aStarFindPath_all_for_deadcace(legalPositions_all_map,
                                           gameState.getAgentPosition(agent.index), point_escape_though_die)
        # actions = gameState.getLegalActions(agent.index)
        if action_choose_though_die not in actions:
            print("送死策略产生非法操作")
            return random.choice(actions)
        return action_choose_though_die
    else:
        if action_choose not in actions:
            print("送死策略产生非法操作")
            return random.choice(actions)
        return action_choose
    return random.choice(actions)


# def level_4_offence(gameState, agent):
#     print("这里是进攻方四阶")


def risk_eat_food_with_enemy(food_first_path_in_escape, gameState, agent):
    # 二阶进攻策略的一部分
    # 注意返回的是action
    # 找到带回避的最近食物后，通过调用这个方法，加入了死路判定，来决定这个食物究竟能不能吃
    # 加入时间判定，看下个食物还来不来得及吃
    enemyList_position_old = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)
    enemyList_position = []
    position_me = gameState.getAgentPosition(agent.index)
    for enemy_position in enemyList_position_old:
        if abs(position_me[0] - enemy_position[0]) + abs(position_me[1] - enemy_position[1]) <= 5:
            enemyList_position.append(enemy_position)
    action_to_food = food_first_path_in_escape[1][-1]
    time_to_food = len(food_first_path_in_escape[1])
    find_closest_escape_point_using_position(agent, gameState, food_first_path_in_escape[0])
    # 上句主要是为了给agent_escape_time赋值，勿删
    if agent.turn_left <= time_to_food + agent.escape_time:
        return "NoTime"
    agent.food_time = time_to_food

    action_choose = find_way_to_nearest_capsule(gameState, agent)
    # print("侦测到危险ghost，开始找吃胶囊的路："+action_choose)
    if action_choose != "NoWayToCapsule":
        find_closest_escape_point_using_position(agent, gameState, position_me)
        # 主要是为了给agent.escape_time赋值，勿删
        if agent.turn_left <= agent.food_time + agent.capsule_time + agent.escape_time:
            return "NoTime"
        if action_choose == action_to_food:
            # print("侦测到危险ghost，开始找吃胶囊的路：" + action_choose+"而且正好能顺路吃个东西")
            return action_choose
        else:
            if check_is_dead_line_risk(agent, gameState, food_first_path_in_escape[0],
                                       enemyList_position, len(food_first_path_in_escape[1])):
                # print("侦测到危险ghost，最近食物为死路，开始找吃胶囊的路：" + action_choose)
                return action_choose
            else:
                # print("先吃东西再找胶囊：" + action_to_food)
                return action_to_food
    else:
        # print("没找到胶囊现在逃跑")
        path_escape = aStarFindPath_forPacman_withAvoid \
            (gameState, find_best_escape_point_using_position \
                (agent, gameState, gameState.getAgentPosition(agent.index)), agent)
        if path_escape != "A*Fail":
            if path_escape == 'Stop':
                # print("目测已经跑到安全地方了")
                return 'SafeNow'
            else:
                action_choose = path_escape.pop()
                if action_choose == action_to_food:
                    # print("没找到胶囊现在逃跑：" + action_choose + "而且正好能顺路吃个东西")
                    return action_choose
                else:
                    if check_is_dead_line_risk(agent, gameState, food_first_path_in_escape[0],
                                               enemyList_position, len(food_first_path_in_escape[1])):
                        # print("最近食物为死路，接着逃吧：" + action_choose)
                        return action_choose
                    else:
                        # print("先吃东西再逃跑：" + action_to_food)
                        return action_to_food
        return "Die"


def value_iteration_offence(gameState, agent):
    foodGrid = agent.getFood(gameState)
    wallGrid = gameState.getWalls()
    # 在原本的value_iteration基础上，加入初步ghost的判断
    # 但这个对ghost的判断，目前来看并不完全准确，先看看效果再说
    if gameState.getAgentState(agent.index).isPacman:
        # 只有自己是pacman的时候，才需要处理幽灵的情况。自己是ghost还怕个鸡儿。
        foodGrid_list = foodGrid.asList()
        enemy_ghost_scared_time_left = getTimeLeft_enemyGhostScared(gameState, agent)
        position_me = gameState.getAgentPosition(agent.index)
        if enemy_ghost_scared_time_left < 1000:
            for food_p in foodGrid_list:
                if agent.getMazeDistance(food_p, position_me) * 2 > enemy_ghost_scared_time_left:
                    foodGrid[food_p[0]][food_p[1]] = False

    # 初始化valueGrid
    valueGrid = wallGrid.copy()
    for i in range(valueGrid.width):
        for j in range(valueGrid.height):
            valueGrid[i][j] = 0.0
    for i in range(wallGrid.width):
        for j in range(wallGrid.height):
            if wallGrid[i][j]:
                valueGrid[i][j] = None
    for i in range(foodGrid.width):
        for j in range(foodGrid.height):
            if foodGrid[i][j]:
                valueGrid[i][j] = 10.0  # 假设一个食物+10，这也是下面计算的出发点
    for j in range(valueGrid.height):
        if valueGrid[agent.middleLine_me][j] is not None:
            valueGrid[agent.middleLine_me][j] = 4.0 * gameState.getAgentState(agent.index).numCarrying
            # 经过计算，每带回一个食物奖励为4

    enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)

    for enemy_p in enemyList_position:
        for i in range(1, valueGrid.width - 1):
            for j in range(1, valueGrid.height - 1):
                if abs(enemy_p[0] - i) + abs(enemy_p[1] - j) <= 5:
                    if valueGrid[i][j] is not None:
                        if (agent.red and i > agent.middleLine_me) or ((not agent.red) and i < agent.middleLine_me):
                            distance_to_enemy = agent.getMazeDistance((i, j), enemy_p)
                            if valueGrid[i][j] > -10.0 + distance_to_enemy:
                                valueGrid[i][j] = -10.0 + distance_to_enemy
        # 10月2日1:50更新敌人值为负值且在迭代中固定下来不改动
    valueGrid_final = value_iteration_2_offence(foodGrid, valueGrid, True)

    (x, y) = gameState.getAgentPosition(agent.index)
    max_value = valueGrid_final[x][y]
    best_action = 'Stop'
    if valueGrid_final[x][y - 1] is not None and valueGrid_final[x][y - 1] > max_value:
        max_value = valueGrid_final[x][y - 1]
        best_action = 'South'
    if valueGrid_final[x][y + 1] is not None and valueGrid_final[x][y + 1] > max_value:
        max_value = valueGrid_final[x][y + 1]
        best_action = 'North'
    if valueGrid_final[x - 1][y] is not None and valueGrid_final[x - 1][y] > max_value:
        max_value = valueGrid_final[x - 1][y]
        best_action = 'West'
    if valueGrid_final[x + 1][y] is not None and valueGrid_final[x + 1][y] > max_value:
        max_value = valueGrid_final[x + 1][y]
        best_action = 'East'
    # print("一阶进攻值迭代的结果"+best_action)
    return best_action


def value_iteration_2_offence(foodGrid, valueGrid, changed):
    if not changed:
        return valueGrid
    else:
        change_flag = False
        valueGrid_new = valueGrid.copy()
        for i in range(1, valueGrid.width - 1):
            for j in range(1, valueGrid.height - 1):
                if (valueGrid[i][j] is not None) and (not foodGrid[i][j]) and (valueGrid[i][j] >= 0.0):
                    valueGrid_new[i][j] = value_iteration_compute_new_offence(valueGrid, i, j)
                    if valueGrid_new[i][j] != valueGrid[i][j]:
                        change_flag = True
        return value_iteration_2_offence(foodGrid, valueGrid_new, change_flag)


def value_iteration_compute_new_offence(valueGrid, x, y):
    max_value = valueGrid[x][y]
    # 此处使用公式 week7-P19。
    influence = 0.8  # 衰变因子
    if valueGrid[x - 1][y] is not None:
        value_west = influence * valueGrid[x - 1][y]
        if value_west > max_value:
            max_value = value_west
    if valueGrid[x + 1][y] is not None:
        value_east = influence * valueGrid[x + 1][y]
        if value_east > max_value:
            max_value = value_east
    if valueGrid[x][y - 1] is not None:
        value_south = influence * valueGrid[x][y - 1]
        if value_south > max_value:
            max_value = value_south
    if valueGrid[x][y + 1] is not None:
        value_north = influence * valueGrid[x][y + 1]
        if value_north > max_value:
            max_value = value_north
    return max_value


def find_best_escape_point_using_position(agent, gameState, position_me):
    # 带回避的寻找回城点
    # 已规约到A*universal
    validPosition = []
    legalPositions = [p for p in gameState.getWalls().asList(False)]
    for p in legalPositions:
        if p[0] == agent.middleLine_me:
            validPosition.append(p)

    enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)
    result_aStar_universal = universal_AStar_with_avoid \
        (agent, gameState, position_me, enemyList_position, validPosition)
    # 返回结果格式为：(goalPosition, path_reverse)
    if result_aStar_universal == "A*Fail":
        return gameState.getAgentState(agent.index).start.getPosition()
    else:
        return result_aStar_universal[0]


def find_closest_escape_point_using_position(agent, gameState, position_me):
    # 不带回避，只算地图距离
    # 更新escape time for capsule。目前只有这个地方有调用
    minDistance = 10000
    minPosition = None
    validPosition = []
    legalPositions = [p for p in gameState.getWalls().asList(False)]
    for p in legalPositions:
        if p[0] == agent.middleLine_me:
            validPosition.append(p)
    for p in validPosition:
        if agent.getMazeDistance(position_me, p) < minDistance:
            minDistance = agent.getMazeDistance(position_me, p)
            agent.escape_time = minDistance
            minPosition = p
    return minPosition


def aStarFindPath_forPacman_withAvoid(gameState, goalPosition, agent):
    # 带规避的A*。注意此处修改为返回整个path list，不能再直接作为action了
    # 已规约到优化版的A*universal
    startPosition = gameState.getAgentPosition(agent.index)
    if startPosition == goalPosition:
        return 'Stop'
    enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)

    result_aStar_universal = universal_AStar_with_avoid \
        (agent, gameState, startPosition, enemyList_position, [goalPosition])
    # 注意universal返回结果格式为：(goalPosition, path_reverse) 或 'A*Fail'
    if result_aStar_universal == "A*Fail":
        return "A*Fail"
    else:
        return result_aStar_universal[1]


def find_way_to_nearest_capsule(gameState, agent):
    # 通过带回避的A*算法得到去胶囊的路径，选择路径最短的那条，返回action
    # 已规约到A*universal
    capsuleList = agent.getCapsules(gameState)
    if len(capsuleList) == 0:
        return "NoWayToCapsule"
    else:
        min_distance_to_capsule = 100000
        best_action = "NoWayToCapsule"
        position_me = gameState.getAgentPosition(agent.index)
        enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)
        result_aStar_universal = universal_AStar_with_avoid \
            (agent, gameState, position_me, enemyList_position, capsuleList)
        # 注意universal返回结果格式为：(goalPosition, path_reverse) 或 'A*Fail'
        if result_aStar_universal != "A*Fail":
            if len(result_aStar_universal[1]) < min_distance_to_capsule:
                min_distance_to_capsule = len(result_aStar_universal[1])
                agent.capsule_time = min_distance_to_capsule
                agent.capsule_position_for_time = result_aStar_universal[0]
                best_action = result_aStar_universal[1].pop()
        return best_action


def find_way_to_nearestFood_with_avoid_and_risk(gameState, agent):
    # 最新定义的返回值为：(目标食物位置， 到目标食物的path_list_reverse)
    # 失败则返回 ("NoWayToFood", "A*Fail")
    # 这个是风险算法，只回避视野内的敌人，而不预判敌人
    # 已规约到A*universal
    startPosition = gameState.getAgentPosition(agent.index)
    foodList = agent.getFood(gameState).asList()
    enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)

    result_aStar_universal = universal_AStar_with_avoid \
        (agent, gameState, startPosition, enemyList_position, foodList)
    # 注意universal返回结果格式为：(goalPosition, path_reverse) 或 'A*Fail'
    if result_aStar_universal != "A*Fail":
        return result_aStar_universal
    else:
        return "NoWayToFood", "A*Fail"


def check_is_dead_line_risk(agent, gameState, position_me_final, enemyList_position, numPath):
    # 原思路是预判所有敌人行动，后改为曼哈顿距离5以内的敌人行动
    # 发现意义还是不大，很少有敌人能根据历史位置预判我的位置，现改为地图距离5以内
    # 优化效率后，又改成曼哈顿距离了。没想到吧.jpg
    legalPositions = [p for p in gameState.getWalls().asList(False)]
    enemyList_position_old = enemyList_position
    enemyList_risk = []
    for enemy_p in enemyList_position_old:
        if abs(gameState.getAgentPosition(agent.index)[0] - enemy_p[0]) + \
                abs(gameState.getAgentPosition(agent.index)[1] - enemy_p[1]) <= 5:
            enemyList_risk.append(enemy_p)
    enemyList_position_old = enemyList_risk

    enemyList_position_new = []
    for enemy_p in enemyList_position_old:
        path_aStarAll_deadLine = aStarFindPath_withPosition_all(legalPositions, enemy_p, position_me_final)
        # 返回格式为：path_reverse = [(position, action)]，注意是倒序。专用于探测死路算法。
        if path_aStarAll_deadLine == 'A*Fail':
            print("不带回避的A*怎么可能失败，请排查")  # 目前只有这一行代码所以不能注释
        else:
            if len(path_aStarAll_deadLine) <= numPath:
                return True
            else:
                enemyList_position_new.append(path_aStarAll_deadLine[-1 * numPath][0])
    enemyList_position_old = enemyList_position_new

    capsuleList = agent.getCapsules(gameState)
    if len(capsuleList) > 0:
        min_distance_to_capsule = 100000
        result_aStar_universal = universal_AStar_with_avoid \
            (agent, gameState, position_me_final, enemyList_position_old, capsuleList)
        # 注意universal返回结果格式为：(goalPosition, path_reverse) 或 'A*Fail'
        if result_aStar_universal != "A*Fail":
            if len(result_aStar_universal[1]) < min_distance_to_capsule:
                return False

    escape_point = find_best_escape_point_using_position(agent, gameState, position_me_final)

    result_aStar_universal = universal_AStar_with_avoid \
        (agent, gameState, position_me_final, enemyList_position_old, [escape_point])
    # 注意universal返回结果格式为：(goalPosition, path_reverse) 或 'A*Fail'
    if result_aStar_universal != "A*Fail":
        return False
    return True


def value_iteration_defence(gameState, agent):
    # 防守方的一阶值迭代

    foodGrid = agent.getFood(gameState)
    wallGrid = gameState.getWalls()

    # 初始化valueGrid
    valueGrid = wallGrid.copy()
    for i in range(valueGrid.width):
        for j in range(valueGrid.height):
            valueGrid[i][j] = 0.0
    for i in range(wallGrid.width):
        for j in range(wallGrid.height):
            if wallGrid[i][j]:
                valueGrid[i][j] = None

    # 虽然没有入侵者位置，但没准能得到边界外的敌人位置
    enemyList_index = agent.getOpponents(gameState)
    enemyList_position = []
    for enemy_index in enemyList_index:
        enemy_position = gameState.getAgentPosition(enemy_index)
        if enemy_position is not None:
            enemyList_position.append(enemy_position)

    if len(enemyList_position) > 0:
        # 如果能知道敌人在哪的话，就去盯防它。甭管谁看到的，敌人必然还没有过界
        for enemy_p in enemyList_position:
            if valueGrid[enemy_p[0]][enemy_p[1]] is not None:
                valueGrid[enemy_p[0]][enemy_p[1]] = 10000  # 勇敢杀敌哟西

    else:
        # 敌人的毛都看不到的时候，找个敌人进攻可能会经过的点蹲着去
        enemy_birth_position = gameState.getAgentState(agent.enemyList_index[0]).start.getPosition()
        foodList_defence = agent.getFoodYouAreDefending(gameState).asList()
        predicted_offence_path_positions = aStar_find_predicted_offence_path_positions(agent, gameState,
                                                                                       enemy_birth_position,
                                                                                       [],
                                                                                       foodList_defence)
        # 返回结果格式为：(goalPosition, [positionList_reverse])
        best_defence_point = None
        if predicted_offence_path_positions == 'A*Fail':
            print("敌人过不来了，我怎么不信呢，估计这步是stop吧")
        else:
            for position in agent.home_positionList:
                if position in predicted_offence_path_positions[1]:
                    best_defence_point = position
                    break
            if valueGrid[best_defence_point[0]][best_defence_point[1]] is not None:
                valueGrid[best_defence_point[0]][best_defence_point[1]] = 10000

    valueGrid_final = value_iteration_2_offence(foodGrid, valueGrid, True)

    if agent.red:
        for i in range(agent.middleLine_me + 1, gameState.getWalls().width - 1):
            for j in range(1, valueGrid_final.height - 1):
                if valueGrid_final[i][j] is not None:
                    valueGrid_final[i][j] = None
    else:
        for i in range(1, agent.middleLine_me):
            for j in range(1, valueGrid_final.height - 1):
                if valueGrid_final[i][j] is not None:
                    valueGrid_final[i][j] = None

    (x, y) = gameState.getAgentPosition(agent.index)
    max_value = valueGrid_final[x][y]
    best_action = 'Stop'
    if valueGrid_final[x][y - 1] is not None and valueGrid_final[x][y - 1] > max_value:
        max_value = valueGrid_final[x][y - 1]
        best_action = 'South'
    if valueGrid_final[x][y + 1] is not None and valueGrid_final[x][y + 1] > max_value:
        max_value = valueGrid_final[x][y + 1]
        best_action = 'North'
    if valueGrid_final[x - 1][y] is not None and valueGrid_final[x - 1][y] > max_value:
        max_value = valueGrid_final[x - 1][y]
        best_action = 'West'
    if valueGrid_final[x + 1][y] is not None and valueGrid_final[x + 1][y] > max_value:
        max_value = valueGrid_final[x + 1][y]
        best_action = 'East'
    # if agent.red:
    #     for j in range(1, valueGrid_final.height - 1):
    #         print("敌方边界：("+str(agent.middleLine_me+1)+","+str(j)+")的值为"+str(valueGrid_final[agent.middleLine_me+1][j]))

    # print(max_value)
    return best_action


def value_iteration_2_defence(valueGrid, changed):
    if not changed:
        return valueGrid
    else:
        changed2 = False
        valueGrid_new = valueGrid.copy()
        for i in range(1, valueGrid.width - 1):
            for j in range(1, valueGrid.height - 1):
                if valueGrid[i][j] is not None:
                    valueGrid_new[i][j] = value_iteration_compute_new_offence(valueGrid, i, j)
                    if valueGrid[i][j] != valueGrid_new[i][j]:
                        changed2 = True
        return value_iteration_2_defence(valueGrid_new, changed2)


def level_1_defender(gameState, agent):
    # 即没有侵略者时执行的动作
    return value_iteration_defence(gameState, agent)


def level_2_defender(gameState, agent):
    # 有侵略者时执行的动作，即有敌人在自己这边
    foodGrid_defence = agent.getFoodYouAreDefending(gameState)
    actions = gameState.getLegalActions(agent.index)
    if len(agent.attackerList_position) > 0:
        # 明确看到敌人位置，也许是自己的视野也许是进攻方的视野
        for attacker_position in agent.attackerList_position:
            path_enemy_escape = universal_AStar_with_avoid(agent, gameState, attacker_position,
                                    [gameState.getAgentPosition(agent.index)],
                                        [gameState.getAgentState(agent.enemyList_index[0]).start.getPosition()])
            if path_enemy_escape == "A*Fail":
                break
        if path_enemy_escape == "A*Fail":
            # print("敌人已死，暂且不动")
            action_choose = 'Stop'
        else:
            action_choose = aStarFindPath_all(agent, agent.legalPositions,
                                          gameState.getAgentPosition(agent.index),
                                          agent.attackerList_position[0])
            # action_choose = value_iteration_defence(gameState, agent, agent.attackerList_position[0])
        agent.foodGrid_defence_lastTime = foodGrid_defence
        if action_choose not in actions:
            print("防御者决定采取非法动作")
            return random.choice(actions)
        # print("看到一个入侵者在" + str(agent.attackerList_position[0]) + "干他！")
        return action_choose
    else:
        # 只知道有敌人但看不到敌人位置，尝试根据失去食物位置得出敌人位置
        foodList_defence = foodGrid_defence.asList()
        foodList_defence_lastTime = agent.foodGrid_defence_lastTime.asList()
        foodList_lost = list(set(foodList_defence_lastTime).difference(set(foodList_defence)))
        agent.foodGrid_defence_lastTime = foodGrid_defence
        if len(foodList_lost) == 0:
            # 看不到敌人位置，也没失去食物，无从推断
            if agent.enemyPosition_lastTime is None:
                # 连上次敌人的位置也没头绪
                action_choose = level_1_defender(gameState, agent)
                if action_choose not in actions:
                    print("防御者决定采取非法动作")
                    return random.choice(actions)
                return action_choose
            else:
                # 本回合没失去食物，但可以追踪上次失去食物的位置
                if agent.getMazeDistance(gameState.getAgentPosition(agent.index), agent.enemyPosition_lastTime) <= 2:
                    # 到了上次的位置附近还是看不到敌人，把上次敌人位置记录清空
                    agent.enemyPosition_lastTime = None
                    action_choose = level_1_defender(gameState, agent)
                    if action_choose not in actions:
                        print("防御者决定采取非法动作")
                        return random.choice(actions)
                else:
                    action_choose = aStarFindPath_all(agent, agent.legalPositions,
                                                      gameState.getAgentPosition(agent.index),
                                                      agent.enemyPosition_lastTime)
                    # action_choose = value_iteration_defence(gameState, agent, agent.enemyPosition_lastTime)
                    if action_choose not in actions:
                        print("防御者决定采取非法动作")
                        return random.choice(actions)
                return action_choose
        else:
            # 本轮失去了食物，通过食物锁定目标
            agent.enemyPosition_lastTime = foodList_lost[0]
            action_choose = aStarFindPath_all(agent, agent.legalPositions,
                                              gameState.getAgentPosition(agent.index),
                                              agent.enemyPosition_lastTime)
            # action_choose = value_iteration_defence(gameState, agent, agent.enemyPosition_lastTime)
            if action_choose not in actions:
                print("防御者决定采取非法动作")
                return random.choice(actions)
            return action_choose


def level_3_defender(gameState, agent):
    # 决定防御者在闪光状态下该去做什么
    # 目前决定让它去进攻，但担心会和进攻方路线重合导致浪费步数，仍需观察验证
    # 此处代码即为进攻方二阶+一阶代码

    enemyList_position = getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent)
    actions = gameState.getLegalActions(agent.index)

    if len(enemyList_position) > 0:
        # 进攻方可以探测到敌人坐标，但也许是防守方发现的
        # 执行二阶进攻策略
        # 目前采取激进二阶策略，只考虑进攻方视野内的敌人
        action_choose = level_2_offence(gameState, agent)
        if action_choose not in actions:
            print("进攻方决定采取非法动作")
            return random.choice(actions)
        return action_choose

    # 到这说明地图上看不到敌人
    # 执行一阶进攻策略
    action_choose = level_1_offence(gameState, agent)
    if action_choose not in actions:
        print("进攻方决定采取非法动作")
        return random.choice(actions)
    return action_choose


def aStarFindPath_all(agent, legalPositions_all_map, startPosition, goalPosition):
    # 单纯算起点到终点的最短路径，注意返回的是单个action
    legalPositions = []
    for position_l in legalPositions_all_map:
        if agent.red:
            if position_l[0] <= agent.middleLine_me:
                legalPositions.append(position_l)
        else:
            if position_l[0] >= agent.middleLine_me:
                legalPositions.append(position_l)
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
                list_reverse = []
                while node[2] > 1:
                    list_reverse.append(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return list_reverse.pop()

            successors = []
            for direction in [Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH]:
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
    return "A*Fail"


def aStarFindPath_all_for_deadcace(legalPositions, startPosition, goalPosition):
    # 单纯算起点到终点的最短路径，注意返回的是单个action
    # 专用于进攻方必死时的送死
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
                list_reverse = []
                while node[2] > 1:
                    list_reverse.append(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return list_reverse.pop()

            successors = []
            for direction in [Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH]:
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
    return "A*Fail"


def aStarFindPath_withPosition_all(legalPositions, startPosition, goalPosition):
    # 不带回避搜寻最短路径，效果同bfs
    # 返回格式为：path_reverse = [(position, action)]，注意是倒序。
    # 此方法为定制型A*。专用于探测死路算法。
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
                list_reverse = []
                while node[2] > 1:
                    list_reverse.append((node[0][0], node[0][1]))
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return list_reverse

            successors = []
            for direction in [Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH]:
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
    return "A*Fail"


def aStar_find_predicted_offence_path_positions(agent, gameState, position_start,
                                                positionList_avoid, positionList_goal):
    # 已优化为一次性A*寻找目标，大大提升运行效率
    # 返回结果格式为：(goalPosition, [positionList_reverse])。注意，正常情况下，这个positionList_reverse是不包括起始点的。
    # 定制型A*。专用于预测敌人进攻路线。
    position_me = position_start
    if position_me in positionList_goal:
        return position_me, [position_me]
    legalPositions_old = [p for p in gameState.getWalls().asList(False)]
    legalPositions = []
    for each_position in legalPositions_old:
        if heuristic_For_universal_AStar(agent, position_me, positionList_avoid, each_position) == 1:
            legalPositions.append(each_position)

    open_list = util.PriorityQueue()
    # (position, action, cost), g(s), self, pre
    open_list.push(((position_me, 'initial', 0), 0, 1, 0),
                   0 + 1)
    count = 2
    best_g = {position_me: 0}
    close_list = []
    visited = [position_me]

    while not open_list.isEmpty():
        node = open_list.pop()
        if (node not in close_list) or (node[1] < best_g[node[0][0]]):
            if node not in close_list:
                close_list.append(node)
            best_g[node[0][0]] = node[1]
            if node[0][0] in positionList_goal:
                goal_position_return = node[0][0]
                list_positions_reverse = []
                while node[2] > 1:
                    list_positions_reverse.append(node[0][0])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return goal_position_return, list_positions_reverse  # goalPosition, path_reverse

            successors = []
            for direction in [Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH]:
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
    return "A*Fail"


def getEnemyPositionList_enemyGhostNotScared_and_enemyPacmanMeScared(gameState, agent):
    # 如果能准确看到敌人的位置，就返回position list；否则返回空list
    # 此处的敌人，仅包括能对我造成伤害的敌人，比如：不闪光的幽灵，加上自己闪光状态下的吃豆人
    enemyList_index = agent.getOpponents(gameState)

    enemyList_position = []
    for enemy_index in enemyList_index:
        if not gameState.getAgentState(enemy_index).isPacman:
            # 如果该敌人是Ghost
            if gameState.getAgentState(enemy_index).scaredTimer == 0:
                # 如果该敌人是Ghost且不闪光
                enemy_position = gameState.getAgentPosition(enemy_index)
                if enemy_position is not None:
                    enemyList_position.append(enemy_position)
        else:
            # 如果该敌人是Pacman
            if gameState.getAgentState(agent.index).scaredTimer > 0:
                # 敌人是Pacman但自己闪光
                enemy_position = gameState.getAgentPosition(enemy_index)
                if enemy_position is not None:
                    enemyList_position.append(enemy_position)
    return enemyList_position


def getTimeLeft_enemyGhostScared(gameState, agent):
    # 如果闪光幽灵在自己的五步内，计算剩余的闪光时间
    # 此处的敌人，仅包括闪光状态下的幽灵敌人，因为这是随一阶策略走的，意味着没有达到二阶判定，所以不会冲突
    # 返回的结果格式为：(position, scaredTimeLeft)。我考虑了一下，只返回那个剩余时间短的好了
    # 我又考虑了一下，还是返回时间吧
    enemyList_index = agent.getOpponents(gameState)
    # position_scaredGhost = None
    time_left = 1000
    for enemy_index in enemyList_index:
        if not gameState.getAgentState(enemy_index).isPacman:
            # 如果该敌人是Ghost
            if gameState.getAgentState(enemy_index).scaredTimer > 0:
                # 如果该敌人是Ghost且处于闪光状态
                enemy_position = gameState.getAgentPosition(enemy_index)
                if enemy_position is not None:
                    if agent.getMazeDistance(enemy_position, gameState.getAgentPosition(agent.index)) <= 5:
                        # 可以观测并且离自己五步以内
                        if gameState.getAgentState(enemy_index).scaredTimer < time_left:
                            time_left = gameState.getAgentState(enemy_index).scaredTimer
                            # position_scaredGhost = enemy_position
    return time_left
    # return position_scaredGhost, time_left


def keep_advantage_offender(gameState, agent):
    # 进攻方的保胜函数。
    # 目前思路是，从对方角度，使用回避算法寻找最优且不在我方防守方视野范围内的食物点
    # 然后使进攻方去守株待兔
    # print("进入进攻方的保胜函数")

    actions = gameState.getLegalActions(agent.index)

    position_teammate = gameState.getAgentPosition(agent.index_teammate)
    attacker_position = None
    for enemy_index in agent.enemyList_index:
        if gameState.getAgentState(enemy_index).isPacman:
            enemy_position = gameState.getAgentPosition(enemy_index)
            if enemy_position is not None:
                if agent.getMazeDistance(position_teammate, enemy_position) <= 5:
                    attacker_position = enemy_position
    if attacker_position is not None:
        path_escape_enemy = universal_AStar_with_avoid\
            (agent, gameState, attacker_position, [position_teammate], agent.home_positionList)
        if path_escape_enemy != 'A*Fail':
            position_escape_enemy = path_escape_enemy[0]
            path_me = aStarFindPath_forPacman_withAvoid(gameState, position_escape_enemy, agent)
            if path_me != 'A*Fail':
                if len(path_me) <= len(path_escape_enemy[1]):
                    action_choose = value_iteration_avoid_teammate\
                        (gameState, agent, attacker_position, position_teammate)
                    if action_choose not in actions:
                        print("五阶进攻中存在非法操作")
                        return random.choice(actions)
                    return action_choose

    action_choose = value_iteration_avoid_teammate(gameState, agent, None, position_teammate)
    if action_choose not in actions:
        print("进攻方五阶失败夭寿了")
        return random.choice(actions)
    return action_choose


def value_iteration_avoid_teammate(gameState, agent, goal_position, teammate_position):
    foodGrid = agent.getFood(gameState)
    wallGrid = gameState.getWalls()

    # 初始化valueGrid
    valueGrid = wallGrid.copy()
    for i in range(valueGrid.width):
        for j in range(valueGrid.height):
            valueGrid[i][j] = 0.0
    for i in range(wallGrid.width):
        for j in range(wallGrid.height):
            if wallGrid[i][j]:
                valueGrid[i][j] = None

    if goal_position is not None:
        # 如果已经有了入侵者位置
        valueGrid[goal_position[0]][goal_position[1]] = 10000
        for i in range(1, valueGrid.width - 1):
            # 加入了回避队友的设定
            for j in range(1, valueGrid.height - 1):
                if abs(teammate_position[0] - i) + abs(teammate_position[1] - j) <= 2:
                    if valueGrid[i][j] is not None:
                        distance_to_teammate = agent.getMazeDistance(teammate_position, (i, j))
                        distance_to_goal = agent.getMazeDistance(goal_position, (i, j))
                        if distance_to_goal > distance_to_teammate:
                            valueGrid[i][j] = -100
    else:
        # 虽然没有入侵者位置，但没准能得到边界外的敌人位置
        enemyList_index = agent.getOpponents(gameState)
        enemyList_position = []
        for enemy_index in enemyList_index:
            enemy_position = gameState.getAgentPosition(enemy_index)
            if enemy_position is not None:
                enemyList_position.append(enemy_position)

        if len(enemyList_position) > 0:
            # 如果能知道敌人在哪的话，就去盯防它。甭管谁看到的，敌人必然还没有过界
            for enemy_p in enemyList_position:
                if valueGrid[enemy_p[0]][enemy_p[1]] is not None:
                    valueGrid[enemy_p[0]][enemy_p[1]] = 10000  # 勇敢杀敌哟西

        else:
            # 敌人的毛都看不到的时候，找个敌人进攻可能会经过的点蹲着去
            enemy_birth_position = gameState.getAgentState(agent.enemyList_index[0]).start.getPosition()
            foodList_defence = agent.getFoodYouAreDefending(gameState).asList()
            predicted_offence_path_positions = aStar_find_predicted_offence_path_positions(agent, gameState,
                                                                                           enemy_birth_position,
                                                                                           [teammate_position],
                                                                                           foodList_defence)
            # 返回结果格式为：(goalPosition, [positionList_reverse])
            best_defence_point = None
            if predicted_offence_path_positions == 'A*Fail':
                print("敌人过不来了，我怎么不信呢，估计这步是stop吧")
            else:
                for position in agent.home_positionList:
                    if position in predicted_offence_path_positions[1]:
                        best_defence_point = position
                        break
                if valueGrid[best_defence_point[0]][best_defence_point[1]] is not None:
                    valueGrid[best_defence_point[0]][best_defence_point[1]] = 10000

        for i in range(1, valueGrid.width - 1):
            # 加入了回避队友的设定
            for j in range(1, valueGrid.height - 1):
                if abs(teammate_position[0] - i) + abs(teammate_position[1] - j) <= 2:
                    if valueGrid[i][j] is not None:
                        valueGrid[i][j] = -100

    valueGrid_final = value_iteration_2_offence(foodGrid, valueGrid, True)

    if agent.red:
        for i in range(agent.middleLine_me + 1, gameState.getWalls().width - 1):
            for j in range(1, valueGrid_final.height - 1):
                if valueGrid_final[i][j] is not None:
                    valueGrid_final[i][j] = None
    else:
        for i in range(1, agent.middleLine_me):
            for j in range(1, valueGrid_final.height - 1):
                if valueGrid_final[i][j] is not None:
                    valueGrid_final[i][j] = None

    (x, y) = gameState.getAgentPosition(agent.index)
    max_value = valueGrid_final[x][y]
    best_action = 'Stop'
    if valueGrid_final[x][y - 1] is not None and valueGrid_final[x][y - 1] > max_value:
        max_value = valueGrid_final[x][y - 1]
        best_action = 'South'
    if valueGrid_final[x][y + 1] is not None and valueGrid_final[x][y + 1] > max_value:
        max_value = valueGrid_final[x][y + 1]
        best_action = 'North'
    if valueGrid_final[x - 1][y] is not None and valueGrid_final[x - 1][y] > max_value:
        max_value = valueGrid_final[x - 1][y]
        best_action = 'West'
    if valueGrid_final[x + 1][y] is not None and valueGrid_final[x + 1][y] > max_value:
        max_value = valueGrid_final[x + 1][y]
        best_action = 'East'

    # print(max_value)
    return best_action


def universal_AStar_with_avoid(agent, gameState, position_me, positionList_avoid, positionList_goal):
    # 通用型带回避的A*算法
    # 已优化为一次性A*寻找目标，大大提升运行效率
    # 返回结果格式为：(goalPosition, path_reverse)
    if position_me in positionList_goal:
        return position_me, ['Stop']
    legalPositions_old = [p for p in gameState.getWalls().asList(False)]
    legalPositions = []
    for each_position in legalPositions_old:
        if heuristic_For_universal_AStar(agent, position_me, positionList_avoid, each_position) == 1:
            legalPositions.append(each_position)

    open_list = util.PriorityQueue()
    # (position, action, cost), g(s), self, pre
    open_list.push(((position_me, 'initial', 0), 0, 1, 0),
                   0 + 1)
    count = 2
    best_g = {position_me: 0}
    close_list = []
    visited = [position_me]

    while not open_list.isEmpty():
        node = open_list.pop()
        if (node not in close_list) or (node[1] < best_g[node[0][0]]):
            if node not in close_list:
                close_list.append(node)
            best_g[node[0][0]] = node[1]
            if node[0][0] in positionList_goal:
                goal_position_return = node[0][0]
                list_reverse = []
                while node[2] > 1:
                    list_reverse.append(node[0][1])
                    for n in close_list:
                        if n[2] == node[3]:
                            node = n
                            break
                return goal_position_return, list_reverse  # goalPosition, path_reverse

            successors = []
            for direction in [Directions.EAST, Directions.WEST, Directions.NORTH, Directions.SOUTH]:
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
    return "A*Fail"


def heuristic_For_universal_AStar(agent, position_me, positionList_avoid, evaluate_position):
    # 最终敌方距离那个参数很关键，必须在2--5之间，越小越倾向冒险接近敌人。
    distance_me = agent.getMazeDistance(position_me, evaluate_position)
    distance_avoidPosition_min = 10000
    avoid_flag = 0
    for position_avoid in positionList_avoid:
        avoid_flag += 1
        distance_avoid = agent.getMazeDistance(position_avoid, evaluate_position)
        if distance_avoid < distance_avoidPosition_min:
            distance_avoidPosition_min = distance_avoid
    if avoid_flag == 0:
        return 1
    else:
        if distance_avoidPosition_min <= distance_me and distance_avoidPosition_min <= 2:
            return 1000
        else:
            return 1


def repeat_detection_for_offender(agent, action):
    # 判断是否横跳。目前仅用于进攻方。反正防守方跟对方进攻方横跳我也没损失。
    if action == Actions.reverseDirection(agent.action_last_turn):
        # 如果该轮行动和上轮行动相反
        if agent.repeat_count >= 4:
            # 已达到横跳次数上限
            agent.repeat_count = 0
            agent.action_last_turn = 'Stop'
            return 'Stop'
        else:
            # 虽然相反，但未达到次数上限
            agent.repeat_count += 1
            agent.action_last_turn = action
            return action
    else:
        # 该轮行动并不和上轮相反
        agent.action_last_turn = action
        agent.repeat_count = 0
        return action
