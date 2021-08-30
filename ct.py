import numpy
from decimal import *
import networkx as nx
import matplotlib.pyplot as plt
import hoprsim



stake = [
   [0, 2, 0, 0, 0, 0, 8, 0, 12, 0], 
   [0, 0, 1, 0, 0, 0, 0, 7, 0, 0], 
   [0, 11, 0, 1, 0, 0, 8, 0, 0, 0], 
   [0, 2, 0, 0, 0, 0, 8, 0, 0, 0],
   [0, 0, 2, 0, 0, 0, 0, 13, 0, 0],
   [0, 0, 0, 14, 9, 0, 0, 5, 0, 0], 
   [0, 0, 0, 23, 6, 0, 0, 0, 9, 0],
   [0, 2, 0, 11, 0, 0, 3, 0, 0, 20],
   [0, 0, 0, 0, 10, 0, 5, 0, 0, 0], 
   [0, 3, 5, 0, 0, 7, 0, 1, 9, 0]  
]

'''
stake = [
   [0, 20, 0], 
   [0, 0, 10], 
   [0, 5, 0]
]
'''

# stake = hoprsim.setupStake(20, 3, 20, 10, 100000, 0.1)
importance = hoprsim.calcImportance(stake)
# print("importance ", importance)
sortedPrioList = [i[0] for i in sorted(enumerate(importance), key=lambda x:x[1], reverse=True)]
print("sortedPrioList", sortedPrioList)



balancePerCtChannel = 5
hops = 3

#ctChannelBalances, ctNodeBalance = hoprsim.openInitialCtChannels(ctNodeBalance, balancePerCtChannel, importance)
#print("channel balances", ctChannelBalances)
numTests = 10
ctNodeBalance = 50
payoutPerHop = 1


def runCT(
    stake,
    numTests=1,
    ctNodeBalance=50,
    payoutPerHop=1,
    hops=3,
    balancePerCtChannel=5
):

    numNodes = len(stake)
    totalPayout = [0] * numNodes
    ctPaths = [0] * numTests

    for w in range(numTests):
        remainingctNodeBalance = ctNodeBalance
        ctChannel = [0] * numNodes
        ctChannelBalances, remainingctNodeBalance = hoprsim.openInitialCtChannels(ctNodeBalance, balancePerCtChannel, importance)
        importanceTmp = list(importance)
        #print("importance", importance)

        # remove all importance entries for nodes to which CT node has no open channels
        for i in range(numNodes):
            if ctChannelBalances[i] == 0 :
                importanceTmp[i] = 0

        pathIndices = [0] * hops
        nodePayout = [0] * numNodes
        for j in range(hops):
            pathIndices[j] = hoprsim.randomPickWeightedByImportance(importanceTmp)

            # reset importance
            importanceTmp = list(importance)

            # give equal payout 1 HOPR reward to nodes selected in the path
            nextNodeIndex = pathIndices[j]
            nodePayout[nextNodeIndex] += payoutPerHop
            totalPayout[nextNodeIndex] += payoutPerHop
            importanceTmp[nextNodeIndex] = 0

            # remove importance entries for nodes to which current hop has no open channels
            # this is used in the path selection for the next hop
            for i in range(numNodes):
                if stake[nextNodeIndex][i] == 0 :
                    importanceTmp[i] = 0

            # store path 
            ctPaths[w] = pathIndices
    listImp = []
    path = sorted(pathIndices)
    print("path", path)
    for i in range(len(stake)):
      s = []
      v = []
      if i in path : 
        for j in range(len(stake)): 
            row = stake[i][:]
            col = stake[:][j]
  
            if (row[j] != 0):
              s.append(j)
              g= set(s) 
              for k in range(len(stake)):
                 if (col[k] != 0):
         
        
                   v.append(k)
                   q= set(v) 
    
        print("list s",i, q) 
        

        sumImportance = 0
        for p in q:
           sumImportance += importance[p]

        print("sum Importance", sumImportance)
        # Now we add those sum of importances of other nodes to each of the path nodes to a list and then we compare them
        # the node from the path that has the largest importance of other nodes with whom it has open channels with is the most strategic one 
        listImp.append(sumImportance)

    #print("list", listImp)

    # find the maximum importance value in this list
    indices = [i for i, x in enumerate(listImp) if x == max(listImp)]
    print("indices", indices)
    maxIndex = 0

    for i in indices:
      for j in indices:
        if (importance[path[i]] > importance[path[j]]):
           maxIndex = i 
        
    print("Best node", path[maxIndex])

    # node with highest payout or a pretty high payout and smaller stake is a positive outlier
    l = []
    r =  []

    for i in range (len(totalPayout)):
    #  find the best positive outlier
      if totalPayout[i] == max(totalPayout):
        bestNode = i
   
      for j in range (len(totalPayout)):
          if (totalPayout[j] > totalPayout[i] and importance[j]< importance[i]):
            l.append(j) 
      m= set(l) 
    print("positive outliers", m)          
    print("Node with highest payout", bestNode)
    return totalPayout, ctPaths

totalPayout, ctPaths = runCT(stake, 10)

print("paths")
hoprsim.printArray2d(ctPaths)

print("stake:")
hoprsim.printArray2d(stake)

print("payout", totalPayout)

totalStake = numpy.sum(stake, axis=1)

print("total stake:")
hoprsim.printArray1d(totalStake)
'''
print("importance", importance)
# exp node 2 has been chosen 20 times for example  
#table = [['total CT Nodes', 'total Payout'], [totalpathIndices, totalPayout]]
#print("table", table)
#accuracyAverage = [0.51,0.52,0.64,0.57,0.7,0.63,0.59,0.66,0.64]
hoprsim.drawGraph(stake)
plt.figure(2)
minMarkerSize = 2
maxMarkerSize = 20
normalizedImportance = [0] * len(importance)
minImportance = min(importance)
maxImportance = max(importance)
for x in range(len(importance)):
    normalizedImportance[x] = float((importance[x] - minImportance) / (maxImportance - minImportance) * (maxMarkerSize - minMarkerSize) + minMarkerSize)
print("normalizedImportance", normalizedImportance)
for x, y, size, text in zip(totalStake, totalPayout, normalizedImportance, range(len(stake))):
    plt.plot(x, y, ms=size, marker='o', color='r', linestyle='None')
    plt.text(x, y, text)
plt.title('Stake vs payout')
plt.xlabel('Stake')
plt.ylabel('Payout')
plt.yscale('log')
plt.xscale('log')
plt.show()
'''
