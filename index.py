from flask import Flask
from flask import render_template
import mysql.connector
import secrets

user = "pythonmgr"
host = "34.65.51.188"
database = "hoprsim"
cnx = mysql.connector.connect(user = user,
                                 password = secrets.password,
                                 host = host,
                                 database = database)
print(cnx)

cursor = cnx.cursor()

query = "SELECT * FROM users"
cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print(row)

cnx.close()


app = Flask(__name__)

@app.route("/")
#def home():
#    return "<h1>gm ser, wgmi!</h1>"

@app.route('/index')
def index():
    name = 'Rosalia'
    return render_template('index.html', title='Welcome', username=name)

app.run(host='0.0.0.0', port=8080)

#if __name__ == "__main__":
#    from waitress import serve
#    serve(app, host="0.0.0.0", port=8080)

