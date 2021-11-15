import hoprsim
import threading

class ctAgent:
    channelsPerCtNode = 2
    ctTickDurationSeconds = 10.0
    hops = 3
    payoutPerHop = 1;

    # ct state
    ctChannelBalances = [] # amounts which the ct node funded towards that channel
    ctChannelRewarded = [] # amount which the node already earned from the respective ctChannelStake,
                           # has to be <= corresponding entry in ctChannelStake
    ctNodeBalance = 0

    def __init__(self, cache, balance=20, channelCount=2, tickDuration=5.0):
        # TODO: add CT node as a normal node including stake matrix etc
        print("Initializing ct agent...")
        self.gameCache = cache
        self.ctNodeBalance = balance
        self.channelsPerCtNode = channelCount
        self.ctTickDurationSeconds = tickDuration
        tokensPerChannel = self.ctNodeBalance / self.channelsPerCtNode
        self.ctChannelBalances, self.ctNodeBalance = hoprsim.openInitialCtChannels(self.ctNodeBalance, tokensPerChannel, self.gameCache.importance)
        self.ctChannelRewarded = [0 for i in range(len(self.ctChannelBalances))]
        print("ct channel balances: ", self.ctChannelBalances)
        print("ct node balance: ", self.ctNodeBalance)
        t = threading.Timer(1, self.tick)
        t.start()
        print("tick duration: ", self.ctTickDurationSeconds)
        print("tick function: ", self.tick)

    def tick(self):
        print("CT tick")
        t = threading.Timer(self.ctTickDurationSeconds, self.tick)
        t.start()
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
