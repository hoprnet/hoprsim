import mysql.connector
import hoprsim

class gameCache:
    # on start, all functions are called directly to initialize global objects

    # just for clarity - summary of all properties that are assigned in respective functions:
    """
    cnx = []            # mySQL connection
    cursor = []         # cursor of mySQL connection
    numPlayers = []     # number of players / rows / columns in stake matrix
    players = []        # raw db dump of users table
    channels = []       # raw db dump of channels table
    stake = []          # stake matrix, square with number of rows & colums equal to numPlayers
    importance = []     # importance list in numpy array format
    importanceList = [] # importance in list format
    playerTable = []    # player table with an added column for importance
    earnings = []       # matrix to indicate which node earned how much from whom
                        # entry in earnings matrix has to be <= the entry in the stake matrix at the same location
                        # if entry in earnings equals the entry in the same location in the stake matrix, the channel is depleted
                        # entry increases whenever some agent sends packet via that edge
                        # entry decreases whenever a node operator takes earnings out and adds them to their balance
                        # table gets resized whenever the player table gets updated
    """

    def __init__(self, connection):
        self.cnx = connection
        self.cursor = self.cnx.cursor()
        self.updateEntireCache()
        self.initializeEarnings()

    def initializeEarnings(self):
        self.earnings = [[0 for i in range(self.numPlayers)] for j in range(self.numPlayers)]

    def increaseEarningsMatrix(self):
        newSize = self.numPlayers
        previousSize = len(self.earnings)
        if (newSize < previousSize):
            print("ERROR: earnings matrix cannot be shrunk!")
        else:
            for i in range(newSize):
                if (i >= previousSize):
                    self.earnings.append([])
                for j in range(newSize):
                    if (i >= previousSize or j >= previousSize):
                        self.earnings[i].append(0)
        hoprsim.printArray2d(self.earnings,0)


    def updateEntireCache(self):
        self.updateNumPlayers()
        self.updatePlayers()
        self.updateChannels()
        self.updateStakeMatrix()
        self.updateImportance()
        self.updatePlayerTable()

    def updateNumPlayers(self):
        query = "SELECT MAX(id) FROM hoprsim.users"
        self.cursor.execute(query)
        result = self.cursor.fetchone()[0]
        if(result == None):
            self.numPlayers = 0
        else:
            self.numPlayers = int(result)
        # TODO: if number decreases -> error, if number increases -> increase earnings matrix

    def updatePlayers(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.players = results;

    def updateChannels(self):
        query = "SELECT * FROM channels"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.channels = results

    def updateStakeMatrix(self):
        self.stake = [[0 for i in range(self.numPlayers)] for j in range(self.numPlayers)]
        for c in self.channels:
            # column 1 in db users table is "fromId", column 2 is "toId", column 3 is "balance"
            if(self.stake[c[1]-1][c[2]-1] != 0):
                print("ERROR! found double entry in stake matrix for channel ", c[1], "-", c[2])
            self.stake[c[1]-1][c[2]-1] = c[3]
        hoprsim

    def updateImportance(self):
        self.importance = hoprsim.calcImportance(self.stake)
        self.importanceList = self.importance.tolist()

    def updatePlayerTable(self):
        self.playerTable = []
        for a in range(len(self.players)):
            playerList = list(self.players[a])
            playerList.append(format(self.importanceList[a], ".2f"))
            # TODO: also append total staked, total unclaimed earnings, number of channels
            self.playerTable.append(playerList)

    def addPlayer(self, name, balance):
        sql = "INSERT INTO users (name, balance) VALUES (%s, %s)"
        values = (name, balance)
        self.cursor.execute(sql, values)
        self.cnx.commit()
        self.updateEntireCache()
        self.increaseEarningsMatrix()

