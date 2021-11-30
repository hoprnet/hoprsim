import hoprsim
import threading
import numpy as np
import datetime

class ctAgent:

    # these values are settings which might also be moved to constructor later?
    tokensPerChannel = 10 # token balance to fund new channels with
    channelCount = 3 # trying to reach this many outgoing channels (or until out of balance, whatever comes first)
    ctTickDurationSeconds = 20.0
    hops = 3 # 3 for routes with 3 intermediate hops
    payoutPerHop = 1 # number of tokens to be paid to each hop
    attemptsPerTick = 10 # number of attempts to find a path of length `hops` before not sending any packet
    routes_indices = [] # sorry for the hack but classes are absolutely retarded to serialize using flask.jsonify
    routes_payouts = []
    routes_ctNodeId = []
    routes_sendTime = []

    # ct state
    ctChannelBalances = [] # amounts which the ct node funded towards that channel
    ctChannelRewarded = [] # amount which the node already earned from the respective ctChannelStake,
                           # has to be <= corresponding entry in ctChannelStake

    def __init__(self, cache, ctNodeId):
        """
        Constructor

        Parameters
        ----------
        cache: a cache with latest state as defined in GameCache.py
        ctNodeId: the ID of the node (as stored in db), that node is not managed by a player but by this agent script
        """
        print("Initializing ct agent...")
        self.gameCache = cache
        self.ctNodeId = ctNodeId - 1 # to transform it from the sql 1-index to the 0-indexed cache
        t = threading.Timer(1, self.tick)
        t.start()

    def openChannels(self):
        #print("opening channels")

        ctNodeStake = self.gameCache.stake[self.ctNodeId]
        print("ct stake: ", ctNodeStake)
        counterPartyEarnings = np.array(self.gameCache.earnings)[:,self.ctNodeId].tolist()
        print("counterparty earnings: ", counterPartyEarnings)

        channelsToBeClosed = []
        # check if any channels are at zero balance
        for i in range(self.gameCache.numPlayers):
            if (ctNodeStake[i] != 0 and ctNodeStake[i] < counterPartyEarnings[i] + self.payoutPerHop * self.hops):
                channelsToBeClosed.append(i)
            elif (ctNodeStake[i] < counterPartyEarnings[i]):
                print("ERROR! ct node stake should never be smaller than earnings of counterparty")

        print("channels to be closed: ", channelsToBeClosed)

        for c in channelsToBeClosed:
            print("closing channel: ", self.ctNodeId + 1, " -> ", c + 1)
            self.gameCache.updateStake(self.ctNodeId + 1, c + 1, 0)

        # check how many channels we have open
        openChannelIds = [i for i, element in enumerate(ctNodeStake) if element!=0]
        print("CT has ", len(openChannelIds), " open channels at indices ", openChannelIds)
        numOpenChannels = len(openChannelIds)
        openChannelIds.append(self.ctNodeId) # add own id to avoid self-staking
        while (numOpenChannels < self.channelCount):

            # do not open channels to same counterparty multiple times
            tmpImportance = list(self.gameCache.importance)
            for i in range(self.gameCache.numPlayers):
                if i in openChannelIds:
                    tmpImportance[i] = 0

            newChannel = hoprsim.randomPickWeightedByImportance(tmpImportance)
            if (newChannel == -1):
                print("ERROR: could not find a counterparty to open the channel to!")
                # TODO: here we should try again but this time including 0 importance nodes
            else:
                print("opening channel to node ", newChannel)
                self.gameCache.updateStake(self.ctNodeId + 1, newChannel + 1, self.tokensPerChannel)
                openChannelIds.append(newChannel)
            # if opening channels didn't work we still want this loop to terminate
            numOpenChannels = numOpenChannels + 1

        emptyChannels = []
        #for channel in channels:


    def sendPacket(self):
        print("sending packet")

        # persist importance list between attempts so that dead ends can be removed
        importanceAttempts = self.gameCache.importance.copy()

        for a in range(self.attemptsPerTick):
            nextNodeIndex = self.ctNodeId
            pathIndices = [nextNodeIndex]

            # try to find a path
            for j in range(self.hops):
                # reset importance
                importanceTmp = importanceAttempts.copy()
                #hoprsim.printArray1d(importanceTmp, 1)

                # remove importance entries for nodes to which current hop has no open channels
                # this is used in the path selection for the next hop
                for i in range(self.gameCache.numPlayers):
                    if self.gameCache.stake[nextNodeIndex][i] == 0 :
                        importanceTmp[i] = 0

                # prevent loops in path by removing existing nodes on path from list
                for i in pathIndices:
                    importanceTmp[i] = 0

                #hoprsim.printArray1d(importanceTmp, 1)
                nextNodeIndex = hoprsim.randomPickWeightedByImportance(importanceTmp)
                if nextNodeIndex == -1:
                    break # stop looking for path if no next node could be found
                pathIndices.append(nextNodeIndex)

            print("Found path: ", pathIndices)
            # then facilitate they payout to each node
            # but only as long as the edge is valid (new earnings + existing earnings <= counter party stake)
            deadEnd = -1
            nodePayouts = []
            if len(pathIndices) == self.hops + 1:
                for hop in range(1,self.hops + 1):
                    # in 3 hop route, 1st relayer gets 3, 2nd gets 2, 3rd gets 1 `payoutPerHop`
                    payout = (self.hops + 1 - hop) * self.payoutPerHop
                    earned = self.gameCache.earnings[pathIndices[hop]][pathIndices[hop-1]]
                    print("earnings for hop ", hop, " are ", earned, ", payout is ", payout)
                    counterPartyStake = self.gameCache.stake[pathIndices[hop-1]][pathIndices[hop]]
                    if earned + payout > counterPartyStake:
                        print("WARNING: ",earned," + ",payout," > stake[", pathIndices[hop-1], "][", pathIndices[hop], "]=", counterPartyStake)
                        break # no further downstream nodes will earn anything
                    self.gameCache.earnings[pathIndices[hop]][pathIndices[hop-1]] += payout
                    nodePayouts.append(payout)
                    #print("earnings now: ", self.gameCache.earnings[pathIndices[hop]][pathIndices[hop-1]])
                    #self.gameCache.updateStake(pathIndices[hop-1]+1, pathIndices[hop]+1, counterPartyStake - payout)
                    #print("earnings now: ", self.gameCache.earnings[pathIndices[hop]][pathIndices[hop-1]])
                break # we found a path so we can stop trying
            elif len(pathIndices) < 2:
                print("ERROR: no path left to try, aborting attempts")
                break
            #else:
            # TODO: exclusion of dead ends like this does not make sense
            #       switch to the heap-based approach as currently implemented in js
            #    print("Found dead end on path, removing node ", pathIndices[1])
            #    importanceAttempts[pathIndices[1]] = 0
        self.routes_indices.append(pathIndices)
        self.routes_payouts.append(nodePayouts)
        self.routes_ctNodeId.append(self.ctNodeId)
        self.routes_sendTime.append(datetime.datetime.utcnow())
        print("path: ", pathIndices)
        #print("earnings:")
        #hoprsim.printArray2d(self.gameCache.earnings, 1)

    def tick(self):
        #print("CT tick")
        self.openChannels()
        self.sendPacket()
        self.nextTick = datetime.datetime.utcnow() + datetime.timedelta(seconds = int(self.ctTickDurationSeconds))
        print("next tick: ", self.nextTick)
        t = threading.Timer(self.ctTickDurationSeconds, self.tick)
        t.start()






