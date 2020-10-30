from gazzettaufficiale import scraper
import json

res = {"series": []}
gu = scraper.GazzettaUfficiale()
for i, s in enumerate(gu.get_latest_series()):
    res["series"].append({"name": s.name, "number": s.number, "publication_date": s.published_date.isoformat(), "elements": []})
    for e in s.get_elements():
        res["series"][i]["elements"].append({
            "title": e.title,
            "publication_date": e.publication_date,
            "section": e.section,
            "law_entity": e.law_entity,
            "short_description": e.short_description,
        })

print(json.dumps(res))
