from datetime import datetime as dt
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


class _BaseObject:
    BASE_URL = "https://www.gazzettaufficiale.it"

    def __init__(self):
        pass

    def _request(self, path):
        res = requests.get(self.BASE_URL + path)
        print(res.url)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup

    @staticmethod
    def _strip_str(input_str: str):
        res = input_str.strip().replace("\n", " ").replace("\t", " ")
        for _ in range(10):
            res = res.replace("  ", " ")
        return res


class Series(_BaseObject):
    def __init__(self, name, number, publication_date):
        super().__init__()
        self.name = name
        self.number = number
        self.publication_date = dt.fromisoformat(publication_date).date()
        self.url = f"/gazzetta/{self.name}/caricaDettaglio/home" \
                   f"?dataPubblicazioneGazzetta={self.publication_date.isoformat()}&" \
                   f"numeroGazzetta={self.number}"

    def __repr__(self):
        return f"<GazzettaUfficiale {self.name} series #{self.number} published the {self.publication_date}>"

    def get_elements(self):
        soup = self._request(self.url)
        spans = soup.find_all("span")[3:]
        section, law_entity = None, None
        elements = []
        for span in spans:
            span_classes = span.attrs.get("class", [])
            if "rubrica" in span_classes:
                section = self._strip_str(span.text)
                continue
            if "emettitore" in span_classes:
                law_entity = self._strip_str(span.text)
                continue
            if "data" in span_classes or "riferimento" in span_classes or "pagina" in span_classes:
                continue

            elements.append(Element(
                title=self._strip_str(span.find("span", {"class": "data"}).text),
                short_description=self._strip_str(span.find_all("a")[-1].contents[0]),
                series=self,
                series_section=section,
                law_entity=law_entity,
            ))
        return elements


class Element(_BaseObject):
    def __init__(self, title, short_description,
                 series: Series, series_section, law_entity):
        super().__init__()
        self.title = title
        self.short_description = short_description
        self.parent_series = series
        self.series_section = series_section
        self.law_entity = law_entity


class GazzettaUfficiale(_BaseObject):
    SERIES = [
        'serie_generale',
        'corte_costituzionale',
        'unione_europea',
        'regioni',
        'concorsi',
        'contratti',
        'parte_seconda',
    ]

    def __init__(self):
        super().__init__()

    def get_latest_series(self):
        soup = self._request("/")
        list_info = soup.find("ul", {"class": "ultimelist"})
        result = []
        for i, item in enumerate(list_info.find_all("li")):
            parsed_item_url = urlparse(item.find("a").attrs.get("href"))
            parsed_qr = parse_qs(parsed_item_url.query)
            result.append(Series(
                name=parsed_item_url.path.split('/')[2],
                number=parsed_qr["numeroGazzetta"][0],
                publication_date=parsed_qr["dataPubblicazioneGazzetta"][0],
            ))
        return result
