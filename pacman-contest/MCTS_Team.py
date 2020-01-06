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
        self.action_last = None
        self.searchTree = None
        '''
        Your initialization code goes here, if you need any.
        '''


    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """

        actions = gameState.getLegalActions(self.index)

        action_choose = uct_for_pacman(gameState, self)
        if action_choose not in actions:
            return random.choice(actions)
        print("This step comes from UCT")
        self.action_last = action_choose
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



  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """

    return "Stop"

    actions = gameState.getLegalActions(self.index)

    return random.choice(actions)



class SearchTreeNode:
    def __init__(self, action, parentNode, gameState, agent):
        self.action = action
        self.parent = parentNode
        self.children = []
        self.q_value = 0
        self.visit = 0
        self.agent = agent
        self.gameState = gameState


def uct_for_pacman(gameState, agent):
    print("start entering uct")
    # root = SearchTreeNode('Root', None, gameState, agent)
    root = agent.searchTree
    if root is None:
        root = SearchTreeNode('Root', None, gameState, agent)
    limit = 5000
    i = 0
    while i < limit:
        leaf = uct_select(root)
        node_withChildren = uct_expand(leaf)
        child = uct_select(node_withChildren)
        child = uct_simulate(child)
        root = uct_backup(child)
        i += 1
    # print_uct_tree(root, 0)
    print_uct_tree(root, 0)

    if len(root.children) == 0:
        print("UCT says there's no way")
        return "UCT_Fail"
    else:
        best_children = [root.children[0]]
        best_value = root.children[0].q_value
        for child in root.children:
            if child.q_value > best_value:
                best_children = []
                best_value = child.q_value
                best_children.append(child)
            if child.q_value == best_value:
                best_children.append(child)
        child_choose = random.choice(best_children)
        agent.searchTree = child_choose
        agent.searchTree.parent = None
        return child_choose.action



# UCT select step
def uct_select(node):
    if len(node.children) == 0:
        return node
    else:
        child_best = node.children[0]
        ucb_best = node.children[0].q_value + 0.2 * ucb_right(node.visit, child_best.visit)
        for child in node.children:
            if child.q_value + 0.2 * ucb_right(node.visit, child.visit) > ucb_best:
                ucb_best = child.q_value + 0.2 * ucb_right(node.visit, child.visit)
                child_best = child
        return uct_select(child_best)
        # return uct_select(random.choice(node.children))

def ucb_right(parentVisit, childVisit):
    if childVisit == 0:
        return 10000
    else:
        return math.sqrt(2.0 * math.log(parentVisit) / childVisit)


# UCT expand step
def uct_expand(node):
    gameState = node.gameState
    agent = node.agent
    legal_actions_old = gameState.getLegalActions(agent.index)
    legal_actions = []
    if node.parent is None:
        action_last_reverse = Actions.reverseDirection(node.agent.action_last)
        for action in legal_actions_old:
            if action != "Stop" and action != action_last_reverse:
                legal_actions.append(action)
        if len(legal_actions) == 0:
            legal_actions.append(action_last_reverse)
    else:
        action_last_reverse = Actions.reverseDirection(node.action)
        for action in legal_actions_old:
            if action != "Stop" and action != action_last_reverse:
                legal_actions.append(action)
        if len(legal_actions) == 0:
            legal_actions.append(action_last_reverse)
    for action in legal_actions:
        gameState_new = gameState.generateSuccessor(agent.index, action)
        child_new = SearchTreeNode(action, node, gameState_new, agent)
        node.children.append(child_new)
    return node


# UCT simulate step
def uct_simulate(node):
    node.q_value = node.agent.getScore(node.gameState)
    return node


# UCT backup step
def uct_backup(node):
    node.visit += 1
    if node.parent is None:
        return node
    else:
        parentNode = node.parent
        max_child_qValue = parentNode.children[0].q_value
        for child_of_parent in parentNode.children:
            if child_of_parent.q_value > max_child_qValue:
                max_child_qValue= child_of_parent.q_value
        parentNode.q_value = -0.05 + 1 * max_child_qValue  # week8-1-P16

        return uct_backup(parentNode)


def print_uct_tree(root, layer):
    if layer < 3:
        i = layer*4
        while i > 0:
            print(" ", end=" ")
            i -= 1
        print(root.action, root.visit, root.q_value)
        for child in root.children:
            print_uct_tree(child, layer+1)

def random_pick(some_list, probabilities):
    x = random.uniform(0,1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
         cumulative_probability += item_probability
         if x < cumulative_probability:
               break
    return item

#get a valid position with the shortest maze distancein in middle line when running away

def runningAway(agent, gameState):

    position = gameState.getAgentPosition(agent.index)
    minDistance = 9999999
    minPosition = (0, 0)
    validPosition = []
    map_game_width = agent.getFood(gameState).width
    legalPositions = [p for p in gameState.getWalls().asList(False)]

    if agent.red:
        middleLine = map_game_width/2-1
    else:
        middleLine = map_game_width/2

    for p in legalPositions:
        if p[0] == middleLine:
            validPosition.append(p)

    for p in validPosition:
        if agent.getMazeDistance(position, p) < minDistance:
            minDistance = agent.getMazeDistance(position, p)
            minPosition = p

    return minPosition
