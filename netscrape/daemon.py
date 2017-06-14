from threading import Thread
import logging

from pymongo.errors import AutoReconnect, ConnectionFailure

from netscrape.utility import utility


class daemon():

    def __init__(self, interface):
        self.util = utility()
        self.interface = interface
        thread = Thread(target=self.start, daemon=True)
        thread.start()

    def start(self):
        try:
            while True:
                peek = self.interface.get_next()
                # Only pop if we have a navigator and its time to pop has come.
                if peek and peek["next"] <= self.util.time_now():
                    # Update next execution time.
                    self.interface.update_navigator(peek["name"], {"next": self.util.time_now() + peek["every"]})
                    if peek["times"] != -1:
                        # Finite number of iterations, decrement times fields.
                        self.interface.update_navigator(peek["name"], {"times": peek["times"] - 1})
                    thread = Thread(target=self.worker, args=(peek,), daemon=True)
                    thread.start()
        except (AutoReconnect, ConnectionFailure):
            logging.exception("Unable to connect to Mongo database. Scheduler cannot get next task.")
        except Exception:
            logging.exception("Scheduler broke on navigator dumped below, followed by stack trace. There is likely a missing field.")

    def worker(self, nav):
        loc = {}
        try:
            exec(nav["function"], {}, loc)
        except Exception as e:
            logging.exception("Failure in internal navigator function for " + nav["name"] + ".")
        if "output" in loc:
            logging.info("Navigator " + nav["name"] + " has scraped the following data:\n" + loc["output"])
        else:
            logging.error("Navigator " + nav["name"] + " does not set 'output' value in its parse function. Failed.")