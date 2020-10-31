from pprint import pprint
from gazzettaufficiale import scraper

# API call mock-up - just for test purposes

res = {"series": []}
gu = scraper.GazzettaUfficiale()
for s in gu.get_latest_series():
    pprint(s.__dict__)
    for e in s.get_elements():
        pprint(e.__dict__)
