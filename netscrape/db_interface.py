from bson.json_util import dumps

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
            "next": args["next"],
            "every": args["every"],
            "times": args["times"],
            "save": args["save"],
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
