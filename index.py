from flask import Flask, render_template, request

import mysql.connector
import secrets
# pip install mysql-connector-python
user = "pythonmgr"
host = "34.65.51.188"
database = "hoprsim"
cnx = mysql.connector.connect(user = user,
                                 password = secrets.password,
                                 host = host,
                                 database = database)

cursor = cnx.cursor()


# obtain all channels and populate stake matrix from that

# render stake matrix

# make own values in cells updateable, validate on client and server side

# run CT every 10 seconds

# list CT paths and payouts over time


#cnx.close()


app = Flask(__name__, static_url_path="/static")

@app.route("/")
@app.route("/index")
def index():
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    return render_template("index.html", members=results)

@app.route("/addPlayer", methods = ["POST"])
def addPlayer():
    name = request.form["name"]
    balance = request.form["balance"]
    print("name: ", name, ", balance: ", balance)
    sql = "INSERT INTO users (name, balance) VALUES (%s, %s)"
    values = (name, balance)
    cursor.execute(sql, values)
    cnx.commit()
    query = "SELECT * FROM users"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    # TODO: query again to get members including the newly added player!
    return render_template("index.html", members=results)

app.run(host="0.0.0.0", port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

