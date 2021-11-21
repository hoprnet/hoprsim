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
    earnings = []       # matrix to indicate from whom (first index to make it compatible with stake)
                        # earned how much from which node (second index)
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
        #for i in range(3):
        #    for j in range(4,6):
        #        self.earnings[i][j] = i*10+j
        #self.earnings[4][8] = 5

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

    """
    if new stake is smaller than counterparty earnings, this function will claim the earnings
    """
    def updateStake(self, fromId, toId, newStake):
        self.claimEarnings(fromId, toId)
        self.claimEarnings(toId, fromId)
        balance = self.players[fromId-1][2]
        currentStake = self.stake[fromId-1][toId-1]
        counterpartyEarnings = self.earnings[toId - 1][fromId - 1]

        if (fromId == toId):
            print("ERROR: tried to self-stake")
            return
        if (currentStake == newStake):
            print("ERROR: same stake amount as before")
            return
        if (currentStake < counterpartyEarnings):
            promt("ERROR: stake less than counterparty earnings, cheata!")
            return

        # check if it's insert, update or delete
        elif (currentStake == 0 and newStake != 0):
            if (balance < newStake):
                print("ERROR: insufficient balance")
                return
            print("adding new channel from ", fromId, " to ", toId, " = ", newStake)
            sql = "INSERT INTO channels (fromId, toId, balance) VALUES (%s, %s, %s)"
            values = (fromId, toId, newStake)
            self.cursor.execute(sql, values)
            self.cnx.commit()

            newBalance = int(balance - newStake)
            print("setting user ", fromId, " balance = ", newBalance)
            sql = "UPDATE users SET balance=%s WHERE id=%s"
            values = (newBalance, fromId)
            self.cursor.execute(sql, values)
            self.cnx.commit()
            # TODO: queries can be executed in one operation

        elif (currentStake != 0 and newStake != 0 and currentStake != newStake):
            # if we increase the stake then we have to make sure to have enough to cover
            if (currentStake < newStake and balance + currentStake < newStake):
                    print("ERROR insufficient balance + current stake for new stake")
                    return

            # reduce their balance
            newBalance = int(balance + currentStake - newStake)
            print("reducing balance of user ", fromId, " to ", newBalance)
            sql = "UPDATE users SET balance=%s WHERE id=%s"
            values = (newBalance, fromId)
            self.cursor.execute(sql, values)
            self.cnx.commit()

            print("updating channel from ", fromId, " to ", toId, " = ", newStake)
            sql = "UPDATE channels SET balance=%s WHERE fromId=%s AND toId=%s"
            values = (newStake, fromId, toId)
            self.cursor.execute(sql, values)
            self.cnx.commit()

        elif (currentStake != 0 and newStake == 0):
            if (newStake < counterpartyEarnings):
                self.claimEarnings(toId, fromId)
            print("deleting channel from ", fromId, " to ", toId)
            sql = "DELETE FROM channels WHERE fromId=%s AND toId=%s"
            values = (fromId, toId)
            self.cursor.execute(sql, values)
            self.cnx.commit()

            newBalance = int(balance + currentStake)
            print("setting balance of user ", fromId, " to ", newBalance)
            sql = "UPDATE users SET balance=%s WHERE id=%s"
            values = (newBalance, fromId)
            self.cursor.execute(sql, values)
            self.cnx.commit()

        self.updateEntireCache()

    def claimEarnings(self, fromId, toId):
        earnings = self.earnings[fromId - 1][toId - 1]
        counterpartyStake = self.stake[toId - 1][fromId - 1]
        if (earnings > counterpartyStake):
            print("ERROR: cannot claim earnings, counter party has too low stake - cheata!")
            return
        if earnings == 0:
            #print("No earnings [", fromId, "][", toId, "]")
            return

        # set remaining counterparty stake in cache
        newStake = int(counterpartyStake - earnings)
        #print("setting stake from ", toId, " to ", fromId, " = ", newStake)
        self.stake[toId - 1][fromId - 1] = newStake

        if newStake == 0:
            sql = "DELETE FROM channels WHERE fromId=%s AND toId=%s"
            values = (toId, fromId)
            self.cursor.execute(sql, values)
            self.cnx.commit()
        else:
            # set remaining counterparty stake in db
            sql = "UPDATE channels SET balance=%s WHERE fromId=%s AND toId=%s"
            values = (newStake, toId, fromId)
            self.cursor.execute(sql, values)
            self.cnx.commit()

        # reset earnings
        self.earnings[fromId - 1][toId - 1] = 0

        # increase balance in db by earnings
        balance = self.players[fromId - 1][2]
        newBalance = int(balance + earnings)
        #print("claiming earnings of user ", fromId, " new balance = ", newBalance)
        sql = "UPDATE users SET balance=%s WHERE id=%s"
        values = (newBalance, fromId)
        self.cursor.execute(sql, values)
        self.cnx.commit()

