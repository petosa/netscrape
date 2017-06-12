import time

from netscrape.navigators.abstract_navigator import abstract_navigator


class google_finance_navigator(abstract_navigator):

    def execute(self):
        print("Executed at " + str(time.time()))

    def save(self):
        print("Meme clock")

    def reschedule(self, scheduler):
        scheduler.add_task(navigator=self, time=time.time() + 5)