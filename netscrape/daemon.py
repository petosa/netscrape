import logging
import json
import time

from bson.json_util import loads, dumps
from threading import Thread
from pymongo.errors import AutoReconnect, ConnectionFailure

from netscrape.utility import utility

class daemon:

    def __init__(self, interface):
        self.interface = interface
        self.utility = utility(self.interface)
        self.alive = True
        thread = Thread(target=self.start)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.alive = False

    def time_now(self):
        return int(round(time.time() * 1000))

    def start(self):
        try:
            while self.alive:
                peek = self.interface.get_next()
                # Only pop if we have a navigator and its time to pop has come.
                if peek and peek["next"] <= self.time_now():
                    # Update next execution time.
                    self.interface.update_navigator(peek["name"], {"next": self.time_now() + peek["every"]})
                    if peek["times"] != -1:
                        # Finite number of iterations, decrement times fields.
                        self.interface.update_navigator(peek["name"], {"times": peek["times"] - 1})
                    thread = Thread(target=self.worker, args=(peek,))
                    thread.daemon = True
                    thread.start()
        except (AutoReconnect, ConnectionFailure):
            logging.exception("Unable to connect to Mongo database. Scheduler cannot get next task.")
            self.critical_scheduler_error()
        except Exception:
            logging.exception("Scheduler broke on navigator dumped below, followed by stack trace. There is likely a missing field.")
            self.critical_scheduler_error()

    def worker(self, nav):
        call_time = self.time_now()
        loc = {}
        try:
            exec(nav["function"], {"utility": self.utility}, loc)
        except Exception as e:
            logging.exception("Failure in internal navigator function for " + nav["name"] + ".")
            self.critical_navigator_error(nav["name"])
        if "output" in loc:
            try:
                parsed_json = loc["output"]
                parsed_bson = loads(json.dumps(loc["output"])) # JSON -> String -> BSON
                #logging.info("Navigator " + nav["name"] + " has scraped the following data:\n" + json.dumps(parsed_json, indent=4))
            except TypeError:
                logging.exception("The output string for navigator " + nav["name"] + " cannot be parsed into JSON.")
                self.critical_navigator_error(nav["name"])
                return
            # Attempt to save
            latest = json.loads(dumps(self.interface.get_newest_data(nav["name"]))) # BSON -> String -> JSON
            try:
                if nav["schema"] and latest: # Only run if this is not the first element to be added to this data collection.
                    assert(self.interface.schema_assertion(parsed_json, latest["data"]))
                self.interface.save_data(nav["name"], parsed_bson, call_time)
                if nav["schema"]:
                    logging.info("SCHEMA PASSED ✔")
                logging.info("SAVED " + nav["name"])
            except AssertionError:
                logging.exception("Schema assertion has failed! The underlying data structure for " + nav["name"] + " has changed.")
                #logging.error("Current schema:\n" + json.dumps(parsed_json, indent=4))
                #logging.error("Old schema:\n" + dumps(latest["data"], indent=4))
                self.critical_navigator_error(nav["name"])
        else:
            logging.error("Navigator " + nav["name"] + " does not set 'output' value in its parse function. Failed.")
            self.critical_navigator_error(nav["name"])

    def critical_navigator_error(self, name):
        logging.error("CRITICAL ERROR: SOMETHING IS FUNDAMENTALLY FLAWED WITH " + name + ". IT DID NOT SCRAPE AND/OR SAVE ITS DATA. FIX OR DELETE IT.")

    def critical_scheduler_error(self):
        logging.error("CRITICAL ERROR: SOMETHING BROKE IN THE SCHEDULER AND IT IS STUCK. FIX IT IMMEDIATELY.")