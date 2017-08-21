from bson.json_util import dumps
import json

from skython.utility import utility


class db_interface():

    # Interface constructor, takes mongo client, the names of the columns we will be using, and optionally Mongo creds.
    def __init__(self, client, system_db, catalog_col, username=None, password=None,):
        self.client = client
        self.system_db = system_db
        self.catalog_col = catalog_col
        self.schedule_col = "schedule"
        if username and password:
            client["admin"].authenticate(username, password)

    # Returns a list of all lambdas in the catalog.
    def get_catalog(self):
        return json.loads(dumps(self.client[self.system_db][self.catalog_col].find()))

    # Given the lambda name, return the corresponding lambda.
    def get_lambda(self, name):
        nav = self.client[self.system_db][self.catalog_col].find({"name": name})
        if nav.count() == 1:
            return json.loads(dumps(nav[0]))
        else:
            return None

    # Given a dictionary of body key values, put that lambda in the catalog.
    def put_lambda(self, args):
        document = {
            "name": args["name"],
            "description": args["description"],
            "args": args["args"],
            "function": args["function"]
        }
        if self.client[self.system_db][self.catalog_col].find({"name": args["name"]}).count() == 0:
            return str((self.client[self.system_db][self.catalog_col].insert_one(document)).inserted_id)
        else:
            return None

    # Run an anonymous function.
    def run_function(self, func, func_args):
        loc = {}
        try:
            inbound_scope = {"utility": utility(self)}
            for item in func_args:
                # Since we don't know whether the user provided us with a string or number, convert to str.
                # Then perform a json.loads to convert dicts and whatnot to objects.
                # Note that this means we cannot pass data that is not JSON compliant.
                inbound_scope[item] = json.loads(str(func_args[item]))
            exec(func, inbound_scope, loc)
            return loc["output"]
        except Exception as e:

            return "Exception in function: " + str(e)

    '''
    def update_lambda(self, name, args):
        update_document = {}
        for key in args:
            if args[key] != None:
                update_document[key] = args[key]
        update = self.client[self.system_db][self.schedule_col].update_one({"name": name}, {"$set": update_document})
        return update.modified_count
    '''

    # Given the name of a lambda, delete it.
    def delete_lambda(self, name):
        result = self.client[self.system_db][self.catalog_col].delete_one({'name': name})
        return result.deleted_count


    # Dangerous! Deletes all lambdas.
    def nuke(self):
        self.client.drop_database(self.system_db)