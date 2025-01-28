from rejestr_produktow_leczniczych_parser import RejestrProduktowLeczniczychParser
from pdf_url_analyzer import PdfUrlAnalyzer
import requests
import pymupdf
import os


# Przykładowe użycie funkcji
def main():
    # Ulotka leku z Rejestru Produktów Leczniczych (rejestry.ezdrowie.gov.pl)
    url = "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/15260/leaflet"
    start_marker = "w jakim celu się go stosuje"
    end_marker = "Informacje ważne przed"


    #Test pdf_url_analyzer.py
    analyzer = PdfUrlAnalyzer(url)
    full_text = analyzer.fetch_pdf_content()
    fragment = analyzer.get_fragment(start_marker, end_marker, min_length=50)

    print(fragment)


    # Test rejestr_produktow_leczniczych_parser.py
    xml_file = "resources/rejestr_produktow_leczniczych.xml"
    if os.path.exists(xml_file):
        print("Plik XML został znaleziony.")
    else:
        print("Plik XML nie został znaleziony. Sprawdź ścieżkę.")
    parser = RejestrProduktowLeczniczychParser(xml_file)


if __name__ == "__main__":
    main()
