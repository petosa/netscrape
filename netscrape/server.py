import json
import sys
import logging
import traceback

from flask import Flask
from pymongo import MongoClient
from flask_restful import reqparse, Api, Resource, abort

from netscrape.daemon import daemon
from netscrape.db_interface import db_interface


class Schedule(Resource):

    def get(self):
        try:
            return json.loads(interface.get_schedule()), 200
        except Exception as e:
            logging.exception("Unable to fulfill get_schedule request.")
            return abort(400, message="Unable to fulfill get_schedule request: " + str(e))

    def put(self):
        try:
            args = parser.parse_args()
            nav = interface.put_navigator(args)
            if nav:
                return nav, 201
            else:
                return "A navigator with the name " + args["name"] + " already exists.", 409
        except Exception as e:
            logging.exception("Unable to fulfill put_navigator request.")
            return abort(400, message="Unable to fulfill put_navigator request: " + str(e))



class Navigator(Resource):

    def get(self, navigator_name):
        try:
            nav = interface.get_navigator(navigator_name)
            if nav:
                return nav, 200
            else:
                return "A navigator with the name " + navigator_name + " does not exist.", 404
        except Exception as e:
            logging.exception("Unable to fulfill get_navigator request for " + navigator_name + ".")
            return abort(400, message="Unable to fulfill get_navigator request for " + navigator_name + ": " + str(e))

    def patch(self, navigator_name):
        try:
            return interface.update_navigator(navigator_name, parser.parse_args())
        except Exception as e:
            logging.exception("Unable to fulfill update_navigator request for " + navigator_name + ".")
            return abort(400, message="Unable to fulfill update_navigator request for " + navigator_name + ": " + str(e))

    def delete(self, navigator_name):
        try:
            return interface.delete_navigator(navigator_name)
        except Exception as e:
            logging.exception("Unable to fulfill delete_navigator request for " + navigator_name + ".")
            return abort(400, message="Unable to fulfill delete_navigator request for " + navigator_name + ": " + str(e))


if __name__ == '__main__':
    client = MongoClient(sys.argv[1])
    system_db = "sys"
    data_db = "data"
    schedule_col = "schedule"

    interface = db_interface(client, system_db, data_db, schedule_col)
    logging.basicConfig(filename='netscrape.log', level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    app = Flask(__name__)
    api = Api(app)

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('next', type=int, required=True)
    parser.add_argument('every', type=int, required=True)
    parser.add_argument('times', type=int, required=True)
    parser.add_argument('save', required=True)
    parser.add_argument('function', required=True)

    api.add_resource(Navigator, '/schedule/<navigator_name>')
    api.add_resource(Schedule, '/schedule')

    d = daemon(interface)
    app.run(debug=False)
