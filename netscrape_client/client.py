import os

from flask import Flask, render_template, send_from_directory
from configparser import ConfigParser

from flask_cors import CORS

config = ConfigParser()
config.read(os.path.join(os.path.dirname( __file__ ), "..", "config.ini"))
FLASK_CLIENT_PORT = int(config["client"]["FLASK_CLIENT_PORT"])
ENDPOINT = config["client"]["ENDPOINT"]

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html", endpoint=ENDPOINT)

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)

@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_CLIENT_PORT)

def get_app():
    return app