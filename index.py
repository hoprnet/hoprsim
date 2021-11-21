from flask import Flask, render_template, request

import mysql.connector
import secrets
# pip install mysql-connector-python

from decimal import *

from threading import Timer

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
ct = ctAgent.ctAgent(myCache, 13)

# TODO:
#
# fix claim & stake UI, should be separate non-transparent overlay with more information and help
# add short explanation for stake table
# render stake numbers with `k`, `m`, `b` and fix column width
# add "cancel" button during edit, dont make these buttons flash
#
# NICE TO HAVES:
# render server-side errors in UI
# do not always go through landing page animation
# only landing page button should flash
# add hover tooltip for stake table
# add animated user guide for first time user

app = Flask(__name__, static_url_path="/static")

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html",
                           members=myCache.playerTable,
                           stake=myCache.stake,
                           earnings=myCache.earnings,
                           )

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
    myCache.earnings[fromId-1][toId-1] = 0
    sql = "UPDATE users SET balance=%s WHERE id=%s"
    values = (int(balance + earnings), fromId)
    myCache.cursor.execute(sql, values)
    myCache.cnx.commit()
    myCache.updateEntireCache()
    return index()

@app.route("/setStake", methods = ["POST"])
def setStake():
    newStake = int(request.form["stakeAmount"])
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    myCache.updateStake(fromId, toId, newStake)
    return index()

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

