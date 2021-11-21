import hoprsim
import threading
import numpy as np

class ctAgent:

    # these values are settings which might also be moved to constructor later?
    tokensPerChannel = 2 # token balance to fund new channels with
    channelCount = 3 # trying to reach this many outgoing channels (or until out of balance, whatever comes first)
    ctTickDurationSeconds = 2.0
    hops = 3 # 3 for routes with 3 intermediate hops
    payoutPerHop = 1; # number of tokens to be paid to each hop

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
        print("importance list: ")
        hoprsim.printArray1d(self.gameCache.importance)
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
            if (ctNodeStake[i] != 0 and ctNodeStake[i] < counterPartyEarnings[i] + self.payoutPerHop):
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

        nodePayout = [0] * self.gameCache.numPlayers
        nextNodeIndex = self.ctNodeId
        pathIndices = [nextNodeIndex]

        for j in range(self.hops):
            # reset importance
            importanceTmp = list(self.gameCache.importance)

            # remove importance entries for nodes to which current hop has no open channels
            # this is used in the path selection for the next hop
            for i in range(self.gameCache.numPlayers):
                if self.gameCache.stake[nextNodeIndex][i] == 0 :
                    importanceTmp[i] = 0

            # prevent loops in path by removing existing nodes on path from list
            for i in pathIndices:
                importanceTmp[i] = 0

            nextNodeIndex = hoprsim.randomPickWeightedByImportance(importanceTmp)
            if nextNodeIndex == -1:
                break # stop looking for path if no next node could be found
            pathIndices.append(nextNodeIndex)

            # give equal payout 1 HOPR reward to nodes selected in the path
            nodePayout[nextNodeIndex] += self.payoutPerHop
            self.gameCache.earnings[nextNodeIndex][pathIndices[-2]] += self.payoutPerHop

            # TODO: in reality the CT node does not know a node's earnings
            #       and it would construct the path regardless
            #       in that case the node upstream of the out-of-funds node
            #       would end up with the additional remaining balance to be forwarded

            # store path
        print("path: ", pathIndices)
        #print("earnings:")
        #hoprsim.printArray2d(self.gameCache.earnings, 1)

    def tick(self):
        #print("CT tick")
        self.openChannels()
        self.sendPacket()
        t = threading.Timer(self.ctTickDurationSeconds, self.tick)
        t.start()

