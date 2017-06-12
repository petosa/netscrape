from netscrape.navigators.abstract_navigator import abstract_navigator
from netscrape.util.html_parse_strategies import html_parse_strategies
import time
from bs4 import BeautifulSoup
import urllib.request

class major_stock_exchange_navigator(abstract_navigator):

    endpoint = "https://en.wikipedia.org/wiki/List_of_stock_exchanges"
    structured_data = None

    def execute(self):
        response = urllib.request.urlopen(self.endpoint)
        soup = BeautifulSoup(response.read(), "lxml")
        table = soup.select_one("table.sortable")
        html_parse_strategies.remove_citations(self, table)
        self.structured_data = html_parse_strategies.htmltable2matrix(self, table)

    def save(self):
        print(self.structured_data)

    def reschedule(self, scheduler):
        scheduler.add_task(navigator=self, time=time.time() + 5)