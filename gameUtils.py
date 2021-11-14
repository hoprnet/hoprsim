import mysql.connector
import hoprsim

class gameCache:
    # on start, all functions are called directly to initialize global objects

    def __init__(self, connection):
        self.cnx = connection
        self.cursor = self.cnx.cursor()
        self.updateEntireCache()

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
        self.numPlayers = int(result)

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
            if(self.stake[c[1]][c[2]] != 0):
                print("ERROR! found double entry in stake matrix for channel ", c[1], "-", c[2])
            self.stake[c[1]][c[2]] = c[3]

    def updateImportance(self):
        self.importance = hoprsim.calcImportance(self.stake)
        self.importanceList = self.importance.tolist()

    def updatePlayerTable(self):
        self.playerTable = []
        for a in range(len(self.players)):
            playerList = list(self.players[a])
            playerList.append(format(self.importanceList[a], ".2f"))
            self.playerTable.append(playerList)

