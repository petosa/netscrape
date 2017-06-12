import pandas as pd

class html_parse_strategies():

    def htmltable2matrix(self, table):
        data = []
        rows = table.select("tr")
        for row in rows:
            temp = []
            cells = row.find_all(["td", "th"])
            for cell in cells:
                temp.append(cell.get_text().strip())
            data.append(temp)
        return pd.DataFrame(data)

    def remove_citations(self, soup):
        for tag in soup.find_all("sup"):
            tag.replaceWith("")