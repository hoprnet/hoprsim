import hoprsim
import threading
import numpy as np

class ctAgent:

    # these values are settings which might also be moved to constructor later?
    tokensPerChannel = 10 # token balance to fund new channels with
    channelCount = 2 # trying to reach this many outgoing channels (or until out of balance, whatever comes first)
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
        # TODO: add CT node as a normal node including stake matrix etc
        print("Initializing ct agent...")
        self.gameCache = cache
        self.ctNodeId = ctNodeId - 1 # to transform it from the sql 1-index to the 0-indexed cache
        t = threading.Timer(self.ctTickDurationSeconds, self.tick)
        t.start()

    def openChannels(self):
        print("opening channels")

        ctNodeStake = self.gameCache.stake[self.ctNodeId]
        print("ct stake: ", ctNodeStake)
        counterPartyEarnings = np.array(self.gameCache.earnings)[:,self.ctNodeId].tolist()
        print("counterparty earnings: ", counterPartyEarnings)

        channelsToBeClosed = []
        # check if any channels are at zero balance
        for i in range(self.gameCache.numPlayers):
            if (ctNodeStake[i] != 0 and ctNodeStake[i] == counterPartyEarnings[i]):
                channelsToBeClosed.append(i)
            elif (ctNodeStake[i] < counterPartyEarnings[i]):
                print("ERROR! ct node stake should never be bigger than earnings of counterparty")

        print("channels to be closed: ", channelsToBeClosed)

        for c in channelsToBeClosed:
            self.gameCache.updateStake(self.ctNodeId, c + 1, 0)

        # check how many channels we have open
        openChannelIds = [i for i, element in enumerate(ctNodeStake) if element!=0]
        print("CT has ", len(openChannelIds), " open channels at indices ", openChannelIds)

        # if not enough -> open more
        #if (len(openChannelIds) < self.channelCount):

        emptyChannels = []
        #for channel in channels:


    def sendPacket(self):
        print("sending packet")
        return
        
        importanceTmp = list(self.gameCache.importance)
        # remove all importance entries for nodes to which CT node has no open channels
        for i in range(self.gameCache.numPlayers):
            if self.ctChannelBalances[i] == 0 :
                importanceTmp[i] = 0

        pathIndices = [0] * self.hops
        nodePayout = [0] * self.gameCache.numPlayers
        for j in range(self.hops):
            nextNodeIndex = hoprsim.randomPickWeightedByImportance(importanceTmp)
            pathIndices[j] = nextNodeIndex

            # reset importance
            importanceTmp = list(self.gameCache.importance)

            # give equal payout 1 HOPR reward to nodes selected in the path
            nodePayout[nextNodeIndex] += self.payoutPerHop
            #totalPayout[nextNodeIndex] += self.payoutPerHop
            #self.gameCache.earnings[nextN
            # TODO: add to earnings in cache

            # remove importance entries for nodes to which current hop has no open channels
            # this is used in the path selection for the next hop
            for i in range(self.gameCache.numPlayers):
                if self.gameCache.stake[nextNodeIndex][i] == 0 :
                    importanceTmp[i] = 0

            # store path
            print("path: ", pathIndices)
            #ctPaths[w] = pathIndices
    # result logs
    ctPaths = []

    # start ct path selection on itertive ticks
    # close channel if out of funds
    # open new channel if we have funds and less channels than limit

    def tick(self):
        print("CT tick")
        self.openChannels()
        self.sendPacket()
        t = threading.Timer(self.ctTickDurationSeconds, self.tick)
        t.start()

