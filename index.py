from flask import Flask, render_template, request

import mysql.connector
import secrets
# pip install mysql-connector-python

from decimal import *

from threading import Timer

import numpy

import hoprsim

import gameUtils

user = "pythonmgr"
host = "34.65.51.188"
database = "hoprsim"
dbConnection = mysql.connector.connect(user = user,
                                 password = secrets.password,
                                 host = host,
                                 database = database)

myCache = gameUtils.gameCache(dbConnection)

# TODO:
# run CT every 10 seconds
# list CT paths and payouts over time
#
# OPTIONAL:
# add "cancel" button during edit, dont make these buttons flash
#
# NICE TO HAVES:
# render server-side errors in UI
# do not always go through landing page animation
# only landing page button should flash
# add hover tooltip for stake table
# add short explanation for stake table
# add animated user guide for first time user

app = Flask(__name__, static_url_path="/static")

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", members=myCache.playerTable, stake=myCache.stake)

@app.route("/addPlayer", methods = ["POST"])
def addPlayer():
    name = request.form["name"]
    balance = request.form["balance"]
    sql = "INSERT INTO users (name, balance) VALUES (%s, %s)"
    values = (name, balance)
    myCache.cursor.execute(sql, values)
    myCache.cnx.commit()
    myCache.updateEntireCache()
    myCache.increaseEarningsMatrix()
    # TODO: also return and render unclaimed earnings matrix
    return render_template("index.html", members=myCache.playerTable, stake=myCache.stake)

@app.route("/setStake", methods = ["POST"])
def setStake():
    stakeAmount = int(request.form["stakeAmount"])
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    balance = myCache.players[fromId-1][2]
    currentStake = myCache.stake[fromId-1][toId-1]

    if (fromId == toId):
        print("ERROR: tried to self-stake")
    elif (currentStake == stakeAmount):
        print("ERROR: same stake amount as before")

    # check if it's insert, update or delete
    elif (currentStake == 0 and stakeAmount != 0):
        if (balance < stakeAmount):
            print("ERROR: insufficient balance")
        else:
            sql = "INSERT INTO channels (fromId, toId, balance) VALUES (%s, %s, %s)"
            values = (fromId, toId, stakeAmount)
            myCache.cursor.execute(sql, values)
            myCache.cnx.commit()

            sql = "UPDATE users SET balance=%s WHERE id=%s"
            values = (int(balance - stakeAmount), fromId)
            myCache.cursor.execute(sql, values)
            myCache.cnx.commit()
            # TODO: queries can be executed in one operation

    elif (currentStake != 0 and stakeAmount != 0 and currentStake != stakeAmount):
        if (currentStake < stakeAmount and balance + currentStake < stakeAmount):
            print("ERROR insufficient balance + current stake")
        else:
            # reduce their balance
            sql = "UPDATE users SET balance=%s WHERE id=%s"
            values = (int(balance + currentStake - stakeAmount), fromId)
            myCache.cursor.execute(sql, values)
            myCache.cnx.commit()

            sql = "UPDATE channels SET balance=%s WHERE fromId=%s AND toId=%s"
            values = (stakeAmount, fromId, toId)
            myCache.cursor.execute(sql, values)
            myCache.cnx.commit()

    elif (currentStake != 0 and stakeAmount == 0):
        sql = "DELETE FROM channels WHERE fromId=%s AND toId=%s"
        values = (fromId, toId)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()

        sql = "UPDATE users SET balance=%s WHERE id=%s"
        values = (int(balance + currentStake), fromId)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()

    myCache.updateEntireCache()
    return render_template("index.html", members=myCache.playerTable, stake=myCache.stake)

# TODO: add functionality to claim earnings from a channel which then get added to the players balance

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

