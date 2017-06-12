import json
import sys
from flask import Flask
from pymongo import MongoClient
from flask_restful import reqparse, request, abort, Api, Resource

from netscrape.daemon import daemon
from netscrape.db_interface import db_interface

client = MongoClient(sys.argv[1])
system_db = "sys"
data_db = "data"
schedule_col = "schedule"

interface = db_interface(client, system_db, data_db, schedule_col)

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('next', type=int)
parser.add_argument('every', type=int)
parser.add_argument('times', type=int)
parser.add_argument('save')
parser.add_argument('function')

class Schedule(Resource):

    def get(self):
        return json.loads(interface.get_schedule()), 200

    def put(self):
        args = parser.parse_args()
        nav = interface.add_navigator(args)
        if nav:
            return nav, 201
        else:
            return "A navigator with the name " + args["name"] + " already exists.", 409


class Navigator(Resource):

    def get(self, navigator_name):
        nav = interface.get_navigator(navigator_name)
        if nav:
            return nav, 200
        else:
            return "A navigator with the name " + navigator_name + " does not exist.", 404

    def patch(self, navigator_name):
        return interface.update_navigator(navigator_name, parser.parse_args())

    def delete(self, navigator_name):
        return interface.delete_navigator(navigator_name)


##
## Actually setup the Api resource routing here
##
api.add_resource(Navigator, '/schedule/<navigator_name>')
api.add_resource(Schedule, '/schedule')


if __name__ == '__main__':
    d = daemon(interface)
    app.run(debug=False)