from bson.json_util import dumps
import json

class db_interface():

    def __init__(self, client, system_db, data_db, schedule_col):
        self.client = client
        self.system_db = system_db
        self.data_db = data_db
        self.schedule_col = schedule_col

    def get_schedule(self):
        return dumps(self.client[self.system_db][self.schedule_col].find())

    def get_navigator(self, name):
        nav = self.client[self.system_db][self.schedule_col].find({"name": name})
        if nav.count() == 1:
            return nav[0]
        else:
            return None

    def put_navigator(self, args):
        document = {
            "name": args["name"],
            "description": args["description"],
            "next": args["next"],
            "every": args["every"],
            "times": args["times"],
            "save": args["save"],
            "schema": args["schema"],
            "function": args["function"]
        }
        if self.client[self.system_db][self.schedule_col].find({"name": args["name"]}).count() == 0:
            return str((self.client[self.system_db][self.schedule_col].insert_one(document)).inserted_id)
        else:
            return None

    def update_navigator(self, name, args):
        update_document = {}
        for key in args:
            if args[key] != None:
                update_document[key] = args[key]
        update = self.client[self.system_db][self.schedule_col].update_one({"name": name}, {"$set": update_document})
        return update.modified_count

    def delete_navigator(self, name):
        result = self.client[self.system_db][self.schedule_col].delete_one({'name': name})
        return result.deleted_count

    # Returns the navigator next in line to be executed. This means that this is the navigator with the smallest next value
    # and which either has a positive or infinite number of runs left.
    def get_next(self):
        return self.client[self.system_db][self.schedule_col].find_one({"$query": {"times": {"$ne": 0}}, "$orderby": {"next": 1}})

    def save(self, name, output, timestamp):
        document = {
            "data": output,
            "creation_date": timestamp
        }
        return str((self.client[self.data_db][name].insert_one(document)).inserted_id)

    # Retrieves the freshes record from the 'name' data collection.
    def get_newest_data(self, name):
        cursor = self.client[self.data_db][name].find().limit(1).sort("creation_date", -1)
        if cursor.count() == 0:
            return None
        return json.loads(dumps(cursor.next()))

    # Boolean function which returns whether the schema of the new data is the same as existing data
    def schema_assertion(self, new_data, old_data):

        def recur(A, B):
            if type(A) is dict and type(B) is dict:
                if A.keys() != B.keys():
                    return False
                for key in A.keys():
                    assert(recur(A[key], B[key]))
            elif type(A) is list and type(B) is list:
                if len(A) > 0 and len(B) > 0:
                    for a in range(len(A)): # Assert that all elements of both lists have the same schema..
                        for b in range(len(B)):
                            assert(recur(A[a], B[b]))
                if len(A) > 1:
                    for x in range(len(A)): # and then make sure all elements of our new list have the same schema.
                        for y in range(len(A)):
                            assert(recur(A[x], A[y]))
            else:
                return type(A) == type(B)
            return True

        try:
            assert(recur(new_data, old_data))
            return True
        except AssertionError:
            return False

    # Return full data history of a navigator
    def get_history(self, name):
        return json.loads(dumps(self.client[self.data_db][name].find().sort("creation_date", -1)))
