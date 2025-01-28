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

    def get_atc_codes(self):
        """
        Zwraca słownik zawierający kody ATC dla każdego produktu.

        Zwraca:
        - Słownik (dict), w którym kluczem jest ID produktu (wartość atrybutu "id" w elemencie
          <produktLeczniczy>), a wartością jest lista kodów ATC z elementów <kodATC> (może być 1 lub więcej kodów).
        """

        atc_mapping = {}
        # Znajdowanie elementów <produktLeczniczy> uwzględniając namespace
        product_elements = self.root.findall("rpl:produktLeczniczy", self.ns)

        for elem in product_elements:
            product_id = elem.get("id", "")
            codes = []
            # Szkaie znacznika <kodyATC> w elemencie <produktLeczniczy>
            kody_atc_elem = elem.find("rpl:kodyATC", self.ns)
            if kody_atc_elem is not None:
                for kod in kody_atc_elem.findall("rpl:kodATC", self.ns):
                    codes.append(kod.text)
            atc_mapping[product_id] = codes

        return atc_mapping
