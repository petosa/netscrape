import logging
import os

from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_restful import reqparse, Api, Resource, abort, inputs
from configparser import ConfigParser

from netscrape.auth import *
from netscrape.daemon import daemon
from netscrape.db_interface import db_interface


# Load config values for server
config = ConfigParser()
config.read(os.path.join(os.path.dirname( __file__ ), "..", "config.ini"))
MONGO_URI = config["server"]["MONGO_URI"]
FLASK_SERVER_PORT = int(config["server"]["FLASK_SERVER_PORT"])
SYSTEM_DB = config["server"]["SYSTEM_DB"]
DATA_DB = config["server"]["DATA_DB"]
SCHEDULE_COL = config["server"]["SCHEDULE_COL"]

# Log configuration
logging.basicConfig(filename=os.path.join(os.path.dirname( __file__ ), "netscrape.log"), level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logging.info("Starting server.")

# Start daemon with configured DB interface
client = MongoClient(MONGO_URI)
if "MONGO_USER" in config["server"] and "MONGO_PASS" in config["server"] != None:
    interface = db_interface(client, SYSTEM_DB, DATA_DB, SCHEDULE_COL, username=config["server"]["MONGO_USER"], password=config["server"]["MONGO_PASS"])
else:
    logging.info("Running without Mongo authentication.")
    interface = db_interface(client, SYSTEM_DB, DATA_DB, SCHEDULE_COL)
daemon(interface)

# Set up body parsing for put
parser = reqparse.RequestParser()
parser.add_argument("name", required=True, help="name field missing. Provide a name for your navigator.")
parser.add_argument("description", required=False)
parser.add_argument("next", type=int, required=True, help="\'next\' field missing. The navigator will run after this timestamp passes.")
parser.add_argument("every", type=int, required=True, help="\'every\' field missing. The navigator will reschedule itself in this many milliseconds.")
parser.add_argument("times", type=int, required=True, help="\'time\' field missing. The navigator will run this many times. Set to -1 for infinite times.")
parser.add_argument("schema", type=inputs.boolean, required=True, help="\'schema\' field missing. Should I check that all saved outputs have the same structure?")
parser.add_argument("function", required=True, help="\'function\' field missing. Function must set the \'output\' variable. You have access to the \'utility\' class.")

# Set up body parsing for update
fuzzy_parser = reqparse.RequestParser()
fuzzy_parser.add_argument("name")
fuzzy_parser.add_argument("description")
fuzzy_parser.add_argument("next", type=int)
fuzzy_parser.add_argument("every", type=int)
fuzzy_parser.add_argument("times", type=int)
fuzzy_parser.add_argument("save", type=inputs.boolean)
fuzzy_parser.add_argument("schema", type=inputs.boolean)
fuzzy_parser.add_argument("function")

# Set up body parsing for testing
test_parser = reqparse.RequestParser()
test_parser.add_argument("function", required=True, help="You must provide a function to test.")

class Schedule(Resource):
    
    @requires_auth
    def get(self):
        return interface.get_schedule(), 200

    @requires_auth
    def put(self):
        args = parser.parse_args()
        nav = interface.put_navigator(args)
        if nav:
            return nav, 201
        else:
            return "A navigator with the name " + args["name"] + " already exists.", 409


class Test(Resource):

    @requires_auth
    def post(self):
        args = test_parser.parse_args()
        output = interface.test_navigator(args)
        return output, 200


class Navigator(Resource):

    @requires_auth
    def get(self, navigator_name):
        nav = interface.get_navigator(navigator_name)
        if nav:
            return nav, 200
        else:
            return "A navigator with the name " + navigator_name + " does not exist.", 404

    @requires_auth
    def patch(self, navigator_name):
        return interface.update_navigator(navigator_name, fuzzy_parser.parse_args())

    @requires_auth
    def delete(self, navigator_name):
        return interface.delete_navigator(navigator_name)


class OneData(Resource):

    @requires_auth
    def get(self, navigator_name):
        nav = interface.get_newest_data(navigator_name)
        if nav:
            return nav, 200
        else:
            return "A navigator with the name " + navigator_name + " does not exist.", 404


class ManyData(Resource):

    @requires_auth
    def get(self, navigator_name):
        nav = interface.get_history(navigator_name)
        if nav:
            return nav, 200
        else:
            return "A navigator with the name " + navigator_name + " does not exist.", 404


class Log(Resource):

    @requires_auth
    def get(self):
        with open(os.path.join(os.path.dirname( __file__ ), "netscrape.log"), "r") as logfile:
            data = logfile.read().replace("\n", "")
        return data, 200


# Create app
app = Flask(__name__)
CORS(app) # Enable CORS
api = Api(app)
api.add_resource(Navigator, "/schedule/<navigator_name>")
api.add_resource(Schedule, "/schedule")
api.add_resource(OneData, "/data/<navigator_name>/top")
api.add_resource(ManyData, "/data/<navigator_name>")
api.add_resource(Test, "/test")
api.add_resource(Log, "/log")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_SERVER_PORT)

def get_app():
    return app
