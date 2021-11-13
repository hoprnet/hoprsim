from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>" + testr(123) + "</h2>"

app.run(host='0.0.0.0', port=8080)
