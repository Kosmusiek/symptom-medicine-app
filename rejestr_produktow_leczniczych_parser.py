# rejestr_produktow_leczniczych_parser.py

import xml.etree.ElementTree as ET


class RejestrProduktowLeczniczychParser:
    """
    Klasa do wczytywania i analizy pliku XML z RPL (Rejestr Produktów Leczniczych)
    Do pobrania - "Rejestr produktów leczniczych - stan na dzień podany w nazwie pliku - całościowy"
    URL:
    https://rejestry.ezdrowie.gov.pl/registry/rpl
    """

    def __init__(self, xml_path):
        """
        Inicjalizuje obiekt parsera XML na podstawie ścieżki do pliku XML.

        Parametry:
        - xml_path (str): Ścieżka do pliku XML.
        """

        self.xml_path = xml_path
        # Wczytanie drzewa XML
        self.tree = ET.parse(self.xml_path)
        # Korzeń dokumentu - <produktyLecznicze>
        self.root = self.tree.getroot()
        # Dodanie namespace do prefiksu 'rpl'
        self.ns = {"rpl": "http://rejestry.ezdrowie.gov.pl/rpl/eksport-danych-v5.0.0"}

    def list_products(self):
        """
        Zwraca listę słowników, z których każdy reprezentuje jeden produkt leczniczy

        Zwraca:
        - Lista słowników zawierających atrybuty elementów <produktLeczniczy>:
          - "nazwaProduktu" (str): Nazwa handlowa produktu.
          - "rodzajPreparatu" (str): Rodzaj preparatu (np. ludzki, weterynaryjny).
          - "nazwaPowszechnieStosowana" (str): Nazwa powszechnie stosowana.
          - "moc" (str): Moc produktu (np. "4 mg/5 ml").
          - "nazwaPostaciFarmaceutycznej" (str): Postać farmaceutyczna.
          - "podmiotOdpowiedzialny" (str): Nazwa podmiotu odpowiedzialnego.
          - "typProcedury" (str): Typ procedury rejestracji (np. DCP).
          - "numerPozwolenia" (str): Numer pozwolenia.
          - "waznoscPozwolenia" (str): Okres ważności pozwolenia.
          - "podstawaPrawna" (str): Podstawa prawna rejestracji.
          - "ulotka" (str): URL do ulotki.
          - "charakterystyka" (str): URL do charakterystyki produktu.
          - "id" (str): Unikalny identyfikator produktu.
        """

        products_data = []
        # Znajdowanie elementów <produktLeczniczy> uwzględniając namespace
        product_elements = self.root.findall("rpl:produktLeczniczy", self.ns)

        for elem in product_elements:
            product_info = {
                "nazwaProduktu": elem.get("nazwaProduktu", ""),
                "rodzajPreparatu": elem.get("rodzajPreparatu", ""),
                "nazwaPowszechnieStosowana": elem.get("nazwaPowszechnieStosowana", ""),
                "moc": elem.get("moc", ""),
                "nazwaPostaciFarmaceutycznej": elem.get("nazwaPostaciFarmaceutycznej", ""),
                "podmiotOdpowiedzialny": elem.get("podmiotOdpowiedzialny", ""),
                "typProcedury": elem.get("typProcedury", ""),
                "numerPozwolenia": elem.get("numerPozwolenia", ""),
                "waznoscPozwolenia": elem.get("waznoscPozwolenia", ""),
                "podstawaPrawna": elem.get("podstawaPrawna", ""),
                "ulotka": elem.get("ulotka", ""),
                "charakterystyka": elem.get("charakterystyka", ""),
                "id": elem.get("id", "")
            }
            products_data.append(product_info)

        return products_data

    def get_url(self, product_id):
        """
        Zwraca krotkę (ulotka_url, charakterystyka_url) dla produktu o zadanym ID.
        Jeśli nie znajdzie produktu, zwraca ("", "").
        """
        product_elem = self.root.find(f"rpl:produktLeczniczy[@id='{product_id}']", self.ns)
        if product_elem is not None:
            ulotka_url = product_elem.get("ulotka", "")
            charakterystyka_url = product_elem.get("charakterystyka", "")
            return (ulotka_url, charakterystyka_url)
        return ("", "")

    def get_info(self, product_id):
        """
        Zwraca słownik z atrybutami produktu o danym ID,
        ale bez kluczy 'ulotka' i 'charakterystyka'.
        Dodatkowo dołącza kody ATC (kodyATC: ["M05BA08", ...]).

        Jeśli nie ma produktu, zwraca pusty słownik.
        """
        product_elem = self.root.find(f"rpl:produktLeczniczy[@id='{product_id}']", self.ns)
        if product_elem is None:
            return {}

        # Atrybuty (bez 'ulotka' i 'charakterystyka')
        info = {
            "nazwaProduktu": product_elem.get("nazwaProduktu", ""),
            "rodzajPreparatu": product_elem.get("rodzajPreparatu", ""),
            "nazwaPowszechnieStosowana": product_elem.get("nazwaPowszechnieStosowana", ""),
            "moc": product_elem.get("moc", ""),
            "nazwaPostaciFarmaceutycznej": product_elem.get("nazwaPostaciFarmaceutycznej", ""),
            "podmiotOdpowiedzialny": product_elem.get("podmiotOdpowiedzialny", ""),
            "typProcedury": product_elem.get("typProcedury", ""),
            "numerPozwolenia": product_elem.get("numerPozwolenia", ""),
            "waznoscPozwolenia": product_elem.get("waznoscPozwolenia", ""),
            "podstawaPrawna": product_elem.get("podstawaPrawna", ""),
            "id": product_elem.get("id", "")
        }

        # Dodaj kody ATC do 'info'
        codes = []
        kody_atc_elem = product_elem.find("rpl:kodyATC", self.ns)
        if kody_atc_elem is not None:
            for kod in kody_atc_elem.findall("rpl:kodATC", self.ns):
                codes.append(kod.text)
        info["kodyATC"] = codes

        return info

