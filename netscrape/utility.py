import csv
import urllib.request


class utility():

    def __init__(self, interface):
        self.interface = interface

    def get_newest_data(self, name):
        return self.interface.get_newest_data(name)

    def get_history(self, name):
        return self.interface.get_history(name)

    def download_page_utf8(self, url):
        return urllib.request.urlopen(url).read().decode("utf-8")

    def download_page(self, url):
        response = urllib.request.urlopen(url)
        return response.read().decode(response.headers.get_content_charset())

    def consume_table(self, table_soup):
        data = []
        headers = table_soup.select("th")
        for row in table_soup.select("tr"):
            document = {}
            for index, cell in enumerate(row.select("td")):
                document[headers[index].get_text().strip()] = cell.get_text().strip()
                print(headers[index].get_text())
                print(cell.get_text())
            if document != {}:
                data.append(document)
        return data

    def consume_csv(self, csv_str):
        cr = csv.reader(csv_str.splitlines(), delimiter=',')
        data = []
        for outer_index, row in enumerate(list(cr)):
            if outer_index == 0:
                header = row
            else:
                document = {}
                for inner_index, cell in enumerate(row):
                    document[header[inner_index]] = cell
                data.append(document)
        return data