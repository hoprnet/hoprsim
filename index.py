from flask import Flask, render_template, request, jsonify

import mysql.connector
import secrets
# pip install mysql-connector-python

from decimal import *

from threading import Timer

import datetime

import numpy

import hoprsim
import gameCache
import ctAgent

user = "pythonmgr"
host = "34.65.51.188"
database = "hoprsim"
dbConnection = mysql.connector.connect(user = user,
                                 password = secrets.password,
                                 host = host,
                                 database = database)

myCache = gameCache.gameCache(dbConnection)
ct = ctAgent.ctAgent(myCache, 1)

# TODO:
# add "new connection" form in player table
# add "cancel" button during edit
#
# NICE TO HAVES:
# render server-side errors in UI
# do not always go through landing page animation
# add hover tooltip for stake table
# add animated user guide for first time user

app = Flask(__name__, static_url_path="/static")

# disable browser caching of content (e.g. CSS / JS) which is annoying for testing 
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

# here we assemble pretty lists on the fly which is better for few page requests and lots of stake/earnings changes (i.e. few users)
# when we have more page loads than stake/earnings changes (i.e. a lot of users refreshing the page)
# then we should re-calculate that on every stake/earnings update
@app.route("/")
@app.route("/index")
def index():
    myCache.updatePlayerTable()
    return render_template("index.html")

@app.route("/addPlayer", methods = ["POST"])
def addPlayer():
    name = request.form["name"]
    balance = request.form["balance"]
    myCache.addPlayer(name, balance)
    return index()

@app.route("/claimEarnings", methods = ["POST"])
def claimEarnings():
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    earnings = myCache.earnings[fromId-1][toId-1]
    balance = myCache.players[fromId-1][2]
    print("earnings: ", earnings)
    if (earnings == 0):
        print("ERROR: no earnings to claim")
    else:
        myCache.earnings[fromId-1][toId-1] = 0
        sql = "UPDATE users SET balance=%s WHERE id=%s"
        values = (int(balance + earnings), fromId)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()
        myCache.updateEntireCache()
    return index()

@app.route("/claimAllEarnings", methods = ["POST"])
def claimAllEarnings():
    fromId = int(request.form["fromId"])
    allEarnings = myCache.earnings[fromId-1]
    balance = myCache.players[fromId-1][2]
    print("all earnings: ", allEarnings)
    totalEarnings = 0
    for i in range(len(allEarnings)):
        earnings = allEarnings[i]
        if earnings > 0:
            myCache.claimEarnings(fromId, i+1)
    #        earnings = myCache.earnings[fromId-1][i]
    #        counterpartyStake = myCache.stake[i][fromId-1]
    #        if earnings > counterpartyStake:
    #            print("ERROR: earnings exceed counterparty stake")
    #            return index()
    #        myCache.earnings[fromId-1][i] = 0
    #        totalEarnings += earnings
    #if totalEarnings == 0:
    #    print("ERROR: no earnings to claim")
    #else:
    #    sql = "UPDATE users SET balance=%s WHERE id=%s"
    #    values = (int(balance + totalEarnings), fromId)
    #    myCache.cursor.execute(sql, values)
    #    myCache.cnx.commit()
    #    myCache.updateEntireCache()
    return index()

@app.route("/setStake", methods = ["POST"])
def setStake():
    newStake = int(request.form["stakeAmount"])
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    myCache.updateStake(fromId, toId, newStake)
    return index()

@app.route("/getCache", methods = ["GET"])
def getCache():
    cache = {
        "members": myCache.playerTable,
        "stake": myCache.stake,
        #"prettyBalance": hoprsim.getPrettyList(list(list(zip(*myCache.playerTable))[2])),
        #"prettyStake": hoprsim.getPrettyMatrix(myCache.stake),
        #"prettyEarnings": hoprsim.getPrettyMatrix(myCache.earnings),
        "earnings": myCache.earnings,
        "routes_indices": ct.routes_indices,
        "routes_payouts": ct.routes_payouts,
        "routes_ctNodeId": ct.routes_ctNodeId,
        "routes_sendTime": ct.routes_sendTime,
        "nextTick": ct.nextTick.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    return jsonify(cache)

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

