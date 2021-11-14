from flask import Flask, render_template, request

import mysql.connector
import secrets
# pip install mysql-connector-python

from decimal import *
import numpy

import hoprsim

user = "pythonmgr"
host = "34.65.51.188"
database = "hoprsim"
cnx = mysql.connector.connect(user = user,
                                 password = secrets.password,
                                 host = host,
                                 database = database)

cursor = cnx.cursor()
def getNumPlayers(cursor):
    query = "SELECT MAX(id) FROM hoprsim.users"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    return result

def getPlayers(cursorr):
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def getChannels(cursor):
    query = "SELECT * FROM channels"
    cursor.execute(query)
    results = cursor.fetchall()
    return results

def getStakeMatrixFromChannels(numPlayers, channels):
    stake = [[0 for i in range(numPlayers)] for j in range(numPlayers)]
    for c in channels:
        if(stake[c[1]][c[2]] != 0):
            print("ERROR! found double entry in stake matrix for channel ", c[1], "-", c[2])
        stake[c[1]][c[2]] = c[3]
    return stake

def calcPlayerTable(players, channels, numPlayers):
    playerTable = []
    players = getPlayers(cursor)
    channels = getChannels(cursor)
    stake = getStakeMatrixFromChannels(numPlayers, channels)
    importance = hoprsim.calcImportance(stake)
    importanceList = importance.tolist()
    for a in range(len(players)):
        playerList = list(players[a])
        playerList.append(format(importanceList[a], ".2f"))
        playerTable.append(playerList)
    print(playerTable)
    return playerTable

numPlayers = getNumPlayers(cursor)
players = getPlayers(cursor)
channels = getChannels(cursor)
stake = getStakeMatrixFromChannels(numPlayers, channels)
hoprsim.printArray2d(stake, 2)
importance = hoprsim.calcImportance(stake)
print(importance)
playerTable = calcPlayerTable(players, channels, numPlayers)

# render stake matrix

# make own values in cells updateable, validate on client and server side

# run CT every 10 seconds

# list CT paths and payouts over time


#cnx.close()


app = Flask(__name__, static_url_path="/static")

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", members=playerTable, stake=stake)

@app.route("/addPlayer", methods = ["POST"])
def addPlayer():
    name = request.form["name"]
    balance = request.form["balance"]
    sql = "INSERT INTO users (name, balance) VALUES (%s, %s)"
    values = (name, balance)
    cursor.execute(sql, values)
    cnx.commit()
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    # TODO: query again to get members including the newly added player!
    return render_template("index.html", members=playerTable, stake=stake)

@app.route("/setStake", methods = ["POST"])
def setStake():
    stakeAmount = int(request.form["stakeAmount"])
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    # check if it's insert, update or delete
    if (stake[fromId][toId] == 0 and stakeAmount != 0):
        print("INSERTING ", fromId, ", ", toId, " = ", stakeAmount)
        sql = "INSERT INTO channels (fromId, toId, balance) VALUES (%s, %s, %s)"
        values = (fromId, toId, stakeAmount)
        cursor.execute(sql, values)
        cnx.commit()
    if (stake[fromId][toId] != 0 and stakeAmount != 0 and stake[fromId][toId] != stakeAmount):
        print("UPDATING ", fromId, ", ", toId, " = ", stakeAmount)
        sql = "UPDATE channels SET balance=%s WHERE fromId=%s AND toId=%s"
        values = (stakeAmount, fromId, toId)
        cursor.execute(sql, values)
        cnx.commit()
    if (stake[fromId][toId] != 0 and stakeAmount == 0):
        print("DELETING ", fromId, ", ", toId)
        sql = "DELETE FROM channels WHERE fromId=%s AND toId=%s"
        values = (fromId, toId)
        cursor.execute(sql, values)
        cnx.commit()
    print("DONE in setStake")
    # TODO: query again to get members including the newly added player!
    return render_template("index.html", members=playerTable, stake=stake)

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

