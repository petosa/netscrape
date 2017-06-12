from threading import Thread
import time
import queue as Q
import traceback

class scheduler():

    backlog = Q.PriorityQueue()

    def __init__(self):
        thread = Thread(target=self.start)
        thread.start()

    def start(self):
        while True:
            # This will block until a new item is available.
            nav_ticket = self.backlog.get()
            # Throw the ticket back if it's not time to process it yet.
            if time.time() < nav_ticket[0]:
                self.backlog.put(nav_ticket)
            else:
                thread = Thread(target=self.worker, args=(nav_ticket[1],))
                thread.start()

    def worker(self, navigator):
        try:
            # Only run save() if execute() succeeds
            navigator.execute()
            navigator.save()
        except Exception as e:
            traceback.print_exc()
        navigator.reschedule(self)

    def add_task(self, time, navigator):
        self.backlog.put([time, navigator])

