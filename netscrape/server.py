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


config = ConfigParser()
config.read(os.path.join(os.path.dirname( __file__ ), "..", "config.ini"))
MONGO_URI = config["server"]["MONGO_URI"]
SERVER_PORT = int(config["server"]["SERVER_PORT"])
SYSTEM_DB = config["server"]["SYSTEM_DB"]
DATA_DB = config["server"]["DATA_DB"]
SCHEDULE_COL = config["server"]["SCHEDULE_COL"]

logging.basicConfig(filename="netscrape.log", level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
app = Flask(__name__)
CORS(app) # Enable CORS
logging.info("Starting server.")
client = MongoClient(MONGO_URI)

if "MONGO_USER" in config["server"] and "MONGO_PASS" in config["server"] != None:
    interface = db_interface(client, SYSTEM_DB, DATA_DB, SCHEDULE_COL, username=config["server"]["MONGO_USER"], password=config["server"]["MONGO_PASS"])
else:
    logging.info("Running without authentication.")
    interface = db_interface(client, SYSTEM_DB, DATA_DB, SCHEDULE_COL)

daemon(interface)

# Set up body parsing for put
parser = reqparse.RequestParser()
parser.add_argument("name", required=True)
parser.add_argument("description", required=False)
parser.add_argument("next", type=int, required=True)
parser.add_argument("every", type=int, required=True)
parser.add_argument("times", type=int, required=True)
parser.add_argument("save", type=inputs.boolean, required=True)
parser.add_argument("schema", type=inputs.boolean, required=True)
parser.add_argument("function", required=True)

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

def service_failed(e):
    logging.exception("Unable to fulfill request. " + str(e))
    return abort(400, message="Unable to fulfill request: " + str(e))


class Schedule(Resource):
    
    @requires_auth
    def get(self):
        try:
            return interface.get_schedule(), 200
        except Exception as e:
            return service_failed(e)

    @requires_auth
    def put(self):
        try:
            args = parser.parse_args()
            nav = interface.put_navigator(args)
            if nav:
                return nav, 201
            else:
                return "A navigator with the name " + args["name"] + " already exists.", 409
        except Exception as e:
            return service_failed(e)


class Navigator(Resource):

    @requires_auth
    def get(self, navigator_name):
        try:
            nav = interface.get_navigator(navigator_name)
            if nav:
                return nav, 200
            else:
                return "A navigator with the name " + navigator_name + " does not exist.", 404
        except Exception as e:
            return service_failed(e)

    @requires_auth
    def patch(self, navigator_name):
        try:
            return interface.update_navigator(navigator_name, fuzzy_parser.parse_args())
        except Exception as e:
            return service_failed(e)

    @requires_auth
    def delete(self, navigator_name):
        try:
            return interface.delete_navigator(navigator_name)
        except Exception as e:
            return service_failed(e)


class OneData(Resource):

    @requires_auth
    def get(self, navigator_name):
        try:
            nav = interface.get_newest_data(navigator_name)
            if nav:
                return nav, 200
            else:
                return "A navigator with the name " + navigator_name + " does not exist.", 404
        except Exception as e:
            return service_failed(e)


class ManyData(Resource):

    @requires_auth
    def get(self, navigator_name):
        try:
            nav = interface.get_history(navigator_name)
            if nav:
                return nav, 200
            else:
                return "A navigator with the name " + navigator_name + " does not exist.", 404
        except Exception as e:
            return service_failed(e)


# Set up routing
api = Api(app)
api.add_resource(Navigator, '/schedule/<navigator_name>')
api.add_resource(Schedule, '/schedule')
api.add_resource(OneData, '/data/<navigator_name>/top')
api.add_resource(ManyData, '/data/<navigator_name>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT)
