from netscrape.utility import utility

page = utility.download_page_utf8("http://www.nasdaq.com/screening/companies-by-region.aspx?region=North+America&exchange=NYSE/companies-by-region.aspx?region=North+America&exchange=NYSE&render=download")
csv = utility.consume_csv(page)

for doc in csv:
    doc.pop('')
    doc.pop('LastSale')
    doc.pop('MarketCap')

output = csv