from flask import Flask, render_template, request

import mysql.connector
import secrets
# pip install mysql-connector-python

from decimal import *
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
# enforce total stake when increasing channel balance
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
    return render_template("index.html", members=myCache.playerTable, stake=myCache.stake)

@app.route("/setStake", methods = ["POST"])
def setStake():
    stakeAmount = int(request.form["stakeAmount"])
    fromId = int(request.form["fromId"])
    toId = int(request.form["toId"])
    # check if it's insert, update or delete
    if (myCache.stake[fromId][toId] == 0 and stakeAmount != 0):
        sql = "INSERT INTO channels (fromId, toId, balance) VALUES (%s, %s, %s)"
        values = (fromId, toId, stakeAmount)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()
    if (myCache.stake[fromId][toId] != 0 and stakeAmount != 0 and myCache.stake[fromId][toId] != stakeAmount):
        sql = "UPDATE channels SET balance=%s WHERE fromId=%s AND toId=%s"
        values = (stakeAmount, fromId, toId)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()
    if (myCache.stake[fromId][toId] != 0 and stakeAmount == 0):
        sql = "DELETE FROM channels WHERE fromId=%s AND toId=%s"
        values = (fromId, toId)
        myCache.cursor.execute(sql, values)
        myCache.cnx.commit()
    myCache.updateEntireCache()
    return render_template("index.html", members=myCache.playerTable, stake=myCache.stake)

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

