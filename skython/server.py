import logging
import os
import json

from flask import Flask, app, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from flask_restful import reqparse, abort, Resource, Api
from configparser import ConfigParser

from skython.auth import *
from skython.db_interface import db_interface


# Load config values for server.
config = ConfigParser()
config.read(os.path.join(os.path.dirname( __file__ ), "..", "config.ini"))
MONGO_URI = config["server"]["MONGO_URI"]
FLASK_SERVER_PORT = int(config["server"]["FLASK_SERVER_PORT"])
SYSTEM_DB = config["server"]["SYSTEM_DB"]
CATALOG_COL = config["server"]["CATALOG_COL"]

# Log configuration.
logging.basicConfig(filename=os.path.join(os.path.dirname( __file__ ), "skython.log"), level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logging.info("Starting server.")

# Create configured DB interface.
client = MongoClient(MONGO_URI)
if "MONGO_USER" in config["server"] and "MONGO_PASS" in config["server"] != None:
    interface = db_interface(client, SYSTEM_DB, CATALOG_COL, username=config["server"]["MONGO_USER"], password=config["server"]["MONGO_PASS"])
else:
    logging.info("Running without Mongo authentication.")
    interface = db_interface(client, SYSTEM_DB, CATALOG_COL)

# A custom type for the argparse type checker. Uses a little trick seen here:
# https://stackoverflow.com/questions/18608812/accepting-a-dictionary-as-an-argument-with-argparse-and-python
def is_dict(val):
    val = json.loads(val)
    assert(type(val) == dict)
    return val

# Set up body parsing for lambda puts.
lambda_parser = reqparse.RequestParser()
lambda_parser.add_argument("name", required=True, help="name field missing. Provide a name for your lambda. ({error_msg})")
lambda_parser.add_argument("description", required=False)
lambda_parser.add_argument("args", required=True, type=is_dict, help="\'args\' field missing or malformed. Function must set the \'args\' dict, mapping the name of each required function arg (a str) to its desciprion (a str). ({error_msg})")
lambda_parser.add_argument("function", required=True, help="\'function\' field missing. Function must set the \'output\' variable. You have access to the \'utility\' class. ({error_msg})")

# Create app.
app = Flask(__name__)
CORS(app) # Enable CORS.

# Conflict error message.
def conflict(message):
    response = jsonify({"message": message})
    response.status_code = 409
    return response

# Not found error message.
def not_found(message):
    response = jsonify({"message": message})
    response.status_code = 404
    return response

# View and add to the catalog.
class Catalog(Resource):
    # Returns a list of all functions in the catalog.
    def get(self):
        return interface.get_catalog(), 200
    # Puts a new function in the catalog.
    @requires_auth
    def put(self):
        args = lambda_parser.parse_args()
        nav = interface.put_lambda(args)
        if nav:
            return nav, 201
        else:
            return conflict("A lambda with the name " + args["name"] + " already exists.")

# Fetching and deleting individual lambdas from the catalog.
class Lambda(Resource):
    # Gets a lambda
    @requires_auth
    def get(self, lambda_name):
        nav = interface.get_lambda(lambda_name)
        if nav:
            return nav, 200
        else:
            return not_found("A lambda with the name " + lambda_name + " does not exist.")
    # Deletes a lambda
    @requires_auth
    def delete(self, lambda_name):
        return interface.delete_lambda(lambda_name)

# Helper for constructor a parser from a dict of required args for a function.
def arg_parser_builder(args, parser):
    for arg in args:
        parser.add_argument(arg, required=True, help="\'" + str(arg) + "\' field missing: " + str(args[arg]) + " ({error_msg})")
    return parser.parse_args()

# Test an anonymous function.
class Test(Resource):
    # Returns the result of a function posted to it.
    @requires_auth
    def post(self):
        test_parser = reqparse.RequestParser()
        test_parser.add_argument("function", required=True, help="You must provide a function to test. ({error_msg})")
        test_parser.add_argument("args", required=True, type=is_dict, help="\'args\' field missing or malformed. Function must set the \'args\' dict, mapping the name of each required function arg (a str) to its desciprion (a str). ({error_msg})")
        func = test_parser.parse_args()["function"]
        args = arg_parser_builder(test_parser.parse_args()["args"], test_parser)
        output = interface.run_function(func, args)
        return output, 200

# Run a lambda from the catalog.
class Run(Resource):
    # Returns the result of the referenced functions given parameters.
    @requires_auth
    def post(self, lambda_name):
        run_parser = reqparse.RequestParser()
        lam = interface.get_lambda(lambda_name)
        if not lam:
            return not_found("A lambda with the name " + lambda_name + " does not exist.")
        func = lam["function"]
        args = arg_parser_builder(lam["args"], run_parser)
        output = interface.run_function(func, args)
        return output, 200

# GET: Fetches the N newest lines of the log file.
# REQUEST PARAM: lines (int) - the number of lines to fetch. Default is 10.
class Log(Resource):
    @requires_auth
    def get(self):
        if "lines" in request.args and request.args["lines"].isdigit():
            num = request.args["lines"]
        else:
            num = 10
        data = os.popen("tail -n " + str(num) + " skython.log").read()
        return Response(data, mimetype='text/plain', status=200)

# Route resources
api = Api(app)
api.add_resource(Catalog, "/catalog")
api.add_resource(Lambda, "/catalog/<lambda_name>")
api.add_resource(Test, "/test")
api.add_resource(Run, "/run/<lambda_name>")
api.add_resource(Log, "/log")

# For testing purposes, manually start app if this file is main. Good for debugging from IDE.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_SERVER_PORT)

# WSGI call to get app reference.
def get_app():
    return app
