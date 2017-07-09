import os

from flask import Flask, render_template, send_from_directory
from configparser import ConfigParser

from flask_cors import CORS

config = ConfigParser()
config.read(os.path.join(os.path.dirname( __file__ ), "..", "config.ini"))
CLIENT_PORT = int(config["client"]["CLIENT_PORT"])
ENDPOINT = config["client"]["ENDPOINT"]

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html", endpoint=ENDPOINT, username="admin", password="secret")

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)

@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


app.run(host='0.0.0.0', port=CLIENT_PORT)
