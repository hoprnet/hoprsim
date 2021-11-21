import networkx as nx
import matplotlib.pyplot as plt
import numpy
from decimal import *

# setting up a stake matrix for a user-defined number of nodes
# random number of channels per node between min and max params

def setupStake(
        # Number of nodes in the network. This number can be changed to test with small and large network size
        numNodes=10,
        # the minimum number of channels a node can open
        minChannelsPerNode=2,
        # the maximum number of channels a node can open 
        maxChannelsPerNode=10,
        minFundsPerNode=10,
        maxFundsPerNode=100,
        tokensPerTicket=0.1
    ):

    stake = [[0 for i in range(numNodes)] for j in range(numNodes)]
    for x in range(numNodes):
        # each node is given a random funding amount
        myFunds = numpy.random.rand() * (maxFundsPerNode - minFundsPerNode) + minFundsPerNode

        # get random number of channels per node
        myChannels = int(numpy.random.rand() * (maxChannelsPerNode - minChannelsPerNode + 1) + minChannelsPerNode)

        # This value represents the amount each node stakes in their channel
        # It is computed as the number of funds a node has divided by number of channels they open
        stakePerChannel = myFunds / myChannels
        stakePerChannel = int(stakePerChannel / tokensPerTicket) * tokensPerTicket

        # fund channels by writing into stake matrix
        for c in range(myChannels):
            # TODO: this does not prevent a node from opening a channel to the same counterparty multiple times
            counterparty = int(numpy.random.rand() * (numNodes - 1))

            # cannot open channel to self - keep diagonal of matrix at 0
            if counterparty >= x:
                counterparty = counterparty + 1
            stake[x][counterparty] = stakePerChannel
            stake = [[Decimal(i) for i in j] for j in stake]

    return stake

def selectChannel(weights, weightIndexToNodeLUT):
    """
    Randomly selects a counterparty based on weights according to a LUT
    Returns the node id (or -1 if none could be found)

    Parameters
    ----------
    weights: a list of weights to be used for normalizing the random selection
    weightIndexToNodeLUT: a LUT translating the weights list to node ids
    """
    rand = numpy.random.rand()
    totalWeight = sum(weights)
    sumWeights = 0
    counterparty = -1
    for i in enumerate(weights):
        sumWeights += i[1]
        if totalWeight == 0:
           sumWeights = 0
        else:
            if sumWeights / totalWeight >= rand:
               counterparty = weightIndexToNodeLUT[i[0]]
               break;
    return counterparty

def calcImportance(stake):

    # get total stake per node
    stakePerNode = [Decimal(sum(e)) for e in stake]

    totalStake = sum(stakePerNode)

    n = len(stake)
    weight = [0] * n
    importance = [0] * n
    for x in range(n):
        for y in range(n):
            # weight of a node is 0 if its stake is equal to 0
            #weight(channel) = sqrt(balance(channel) / stake(channel.source) * stake(channel.destination))
            weight[y] += 0 if stakePerNode[y]==0 else numpy.sqrt(stake[y][x]/stakePerNode[y] * stakePerNode[x])

    #print("Weighted downstream stake per node p(n) = ", weight)
    importanceList = numpy.array(weight) * numpy.array(stakePerNode)
    return importanceList;



# pick a random node based on its importance
def randomPickWeightedByImportance(importance):

    channel = selectChannel(importance, [i for i in range(len(importance))])
    return channel



# opens a random payment channel given its importance
def openInitialCtChannels(ctNodeBalance, balancePerCtChannel, importance):
    ctChannelBalances = [0 for i in range(len(importance))]
    while (ctNodeBalance >= balancePerCtChannel):
        ctChannelBalances[randomPickWeightedByImportance(importance)] += balancePerCtChannel
        ctNodeBalance -= balancePerCtChannel
    return ctChannelBalances, ctNodeBalance



def drawGraph(stake):
    """
    draws a network graph based on a square stake matrix with 0-diagonale
    the stake matrix has channel opener in rows and counterparty in columns
    each entry in the stake matrix represents the value staked in channel (0 for no channel)

    Parameters
    ----------
    stake: stake matrix
    """
    # parameters for drawing
    minLineWeight = 1
    maxLineWeight = 4
    blue1 = '#0000b4'
    blue2 = '#b4f0ff'
    blue3 = '#000050'
    blue4 = '#3c64a5'
    yellow = '#ffffa0'
    edgeColorA = blue1
    edgeColorB = blue4
    nodeColor = yellow
    nodeSize = 500
    labelFont = 'Source Code Pro'
    connectionstyle = 'arc3, rad=0.0'
    arrowstyle = '->'
    # /parameters

    G=nx.OrderedDiGraph()
    stake1d = numpy.concatenate(stake)
    maxS = max(stake1d)
    minS = min(stake1d[numpy.nonzero(stake1d)])
    bottomEdges = []
    topEdges = []
    bottomWeights = []
    topWeights = []
    bottomColors = []
    topColors = []
    print("maxS: ", maxS)
    print("minS: ", minS)

    for x in range(len(stake)):
        for y in range(x):
            weightA = 0
            weightB = 0
            if(stake[x][y] > 0):
                weightA = (stake[x][y] - minS) / (maxS - minS) * (maxLineWeight - minLineWeight) + minLineWeight
                G.add_edge(x, y, weight=weightA, color=edgeColorA)
            if(stake[y][x] > 0):
                weightB = (stake[y][x] - minS) / (maxS - minS) * (maxLineWeight - minLineWeight) + minLineWeight
                G.add_edge(y, x, weight=weightB, color=edgeColorB)

        # plot in the right order to have the fatter edge on the bottom
            if(weightA > 0 and weightB > 0):
                if(weightA > weightB):
                    bottomEdges.append((x,y))
                    topEdges.append((y,x))
                    bottomWeights.append(weightA)
                    topWeights.append(weightB)
                    bottomColors.append(edgeColorA)
                    topColors.append(edgeColorB)
                else:
                    bottomEdges.append((y,x))
                    topEdges.append((x,y))
                    bottomWeights.append(weightB)
                    topWeights.append(weightA)
                    bottomColors.append(edgeColorB)
                    topColors.append(edgeColorA)
            elif(weightA > 0):
                topEdges.append((x,y))
                topWeights.append(weightA)
                topColors.append(edgeColorA)
            elif(weightB > 0):
                topEdges.append((y,x))
                topWeights.append(weightB)
                topColors.append(edgeColorB)

    weights = list(nx.get_edge_attributes(G,'weight').values())
    colors = list(nx.get_edge_attributes(G,'color').values())
    pos = nx.circular_layout(G)

    nx.draw_networkx_nodes(G, pos, node_size=nodeSize, node_color=nodeColor)
    nx.draw_networkx_labels(G, pos, font_family=labelFont)
    nx.draw_networkx_edges(
        G,
        pos=pos,
        width=bottomWeights,
        edge_color=bottomColors,
        edgelist=bottomEdges,
        arrows=True,
        connectionstyle=connectionstyle,
        arrowstyle=arrowstyle
    )
    nx.draw_networkx_edges(
        G,
        pos=pos,
        width=topWeights,
        edge_color=topColors,
        edgelist=topEdges,
        arrows=True,
        connectionstyle=connectionstyle,
        arrowstyle=arrowstyle
    )

#    plt.show()


def printArray2d(a, format=1):
    for row in range(len(a)):
        for col in range (len(a[row])):
            if format == 1:
                print("{:4.1f}".format(a[row][col]), end = " ")
            else:
                print("{:4.0f}".format(a[row][col]), end = " ")

        print()



def printArray1d(a, format=1):
    for row in range(len(a)):
        if format == 1:
            print("{:4.1f}".format(a[row]), end = " ")
        else:
            print("{:4.0f}".format(a[row]), end = " ")

    print()



def runCT(
    stake,
    numTests=10,
    ctNodeBalance=50,
    payoutPerHop=1,
    hops=3,
    balancePerCtChannel=5
):
    """
    starts cover traffic

    Parameters:
    -----------
    stake: stake matrix
    numTests: number of iterations to run (starts with opening channels from CT node)
    ctNodeBalance: number of tokens on CT node
    payoutPerHop: number of tokens to be paid out to each node along a selected path
    hops: number of hops per path
    balancePerCtChannel: CT node funds each channel with this many tokens (subtracted from ctNodeBalance)
    """
    numNodes = len(stake)
    totalPayout = [0] * numNodes
    ctPaths = [0] * numTests
    importance = calcImportance(stake)

    for w in range(numTests):
        remainingctNodeBalance = ctNodeBalance
        ctChannel = [0] * numNodes
        ctChannelBalances, remainingctNodeBalance = openInitialCtChannels(ctNodeBalance, balancePerCtChannel, importance)
        importanceTmp = list(importance)

        # remove all importance entries for nodes to which CT node has no open channels
        for i in range(numNodes):
            if ctChannelBalances[i] == 0 :
                importanceTmp[i] = 0

        pathIndices = [0] * hops
        nodePayout = [0] * numNodes
        for j in range(hops):
            nextNodeIndex = randomPickWeightedByImportance(importanceTmp)
            pathIndices[j] = nextNodeIndex

            # reset importance
            importanceTmp = list(importance)

            # give equal payout 1 HOPR reward to nodes selected in the path
            nodePayout[nextNodeIndex] += payoutPerHop
            totalPayout[nextNodeIndex] += payoutPerHop

            # remove importance entries for nodes to which current hop has no open channels
            # this is used in the path selection for the next hop
            for i in range(numNodes):
                if stake[nextNodeIndex][i] == 0 :
                    importanceTmp[i] = 0

            # store path 
            ctPaths[w] = pathIndices
    return totalPayout, ctPaths

def prettyNumber(number):
    divisor = 1
    prefix = ""
    decimals = 0
    if number >= 1e9:
        divisor = 1e9
        prefix = "G"
    elif number >= 1e6:
        divisor = 1e6
        prefix = "M"
    elif number >= 1e3:
        divisor = 1e3
        prefix = "k"

    if number < 1e3:
        decimals = 0
    elif number >= 1e3 and number < 10e3:
        decimals = 1
    elif number >= 10e3 and number < 1e6:
        decimals = 0
    elif number >= 1e6 and number < 10e6:
        decimals = 1
    elif number >= 10e6 and number < 1e9:
        decimals = 0
    elif number >= 1e9 and number < 10e9:
        decimals = 1
    prettyNumber = format(number/divisor, "." + str(decimals) + "f") + prefix
    return prettyNumber

def getPrettyMatrix(uglyMatrix):
    prettyMatrix = [[prettyNumber(uglyMatrix[j][i]) for i in range(len(uglyMatrix))] for j in range(len(uglyMatrix))]
    return prettyMatrix

def getPrettyList(uglyList):
    print("ugly list: ", uglyList)
    prettyList = [prettyNumber(uglyList[i]) for i in range(len(uglyList))]
    return prettyList
