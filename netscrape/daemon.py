from threading import Thread

from netscrape.utility import utility


class daemon():

    def __init__(self, interface):
        self.util = utility()
        self.interface = interface
        thread = Thread(target=self.start)
        thread.start()

    def start(self):
        while True:
            peek = self.interface.get_next()
            # Only pop if we have a navigator and its time to pop has come.
            if peek and peek["next"] <= self.util.time_now():
                times = peek["times"]
                if times != -1:
                    # Update top record to decrement its time and set next execution time.
                    self.interface.update_navigator(peek["name"], {"times": peek["times"] - 1, "next": self.util.time_now() + peek["every"]})
                else:
                    # Just update next execution time. This will only run on records with a -1 time setting (infinity).
                    self.interface.update_navigator(peek["name"], {"next": self.util.time_now() + peek["every"]})
                loc = {}
                exec(peek["function"], {}, loc)
                if "output" in loc:
                    print(loc["output"])
                else:
                    print(KeyError("Make sure a variable named 'output' contains your final parsed in your navigator function. Failed."))