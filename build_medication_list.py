# build_medication_list.py - skrypt do tworzenia listy leków z pliku XML

import csv
import os

from rejestr_produktow_leczniczych_parser import RejestrProduktowLeczniczychParser
from pdf_url_analyzer import PdfUrlAnalyzer

def build_medication_list(xml_file, output_csv, start_marker="w jakim celu się go stosuje", end_marker="Informacje ważne przed", min_length=20):
    """
    Tworzy listę leków ('rodzajPreparatu' == 'ludzki'), pobiera z PDF (ulotki) opis między znacznikami i zapisuje w pliku CSV.

    Parametry:
    - xml_file (str): ścieżka do pliku XML z listą produktów.
    - output_csv (str): ścieżka do pliku CSV, gdzie wynik zostanie zapisany.
    - start_marker (str): znacznik początkowy w ulotce.
    - end_marker (str): znacznik końcowy w ulotce.
    - min_length (int): minimalna długość znalezionego fragmentu.
    """

    # Sprawdzenie, czy plik XML istnieje
    if not os.path.exists(xml_file):
        print(f"Brak pliku XML: {xml_file}")
        return

    # Parsowanie pliku XML
    parser = RejestrProduktowLeczniczychParser(xml_file)
    products = parser.list_products()
    print(f"Załadowano {len(products)} produktów z pliku XML.")

    # Filtrowanie produktów po 'rodzajPreparatu' == 'ludzki'
    products = [p for p in products if p["rodzajPreparatu"].lower() == "ludzki"]
    print(f"W tym {len(products)} produktów z wartością 'rodzajPreparatu' == 'ludzki'.")

    # Otwarcie pliku CSV do zapisu
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        # Nagłówki
        writer.writerow(["id", "nazwaProduktu", "nazwaPowszechnieStosowana", "opis"])

        # Pobranie fragmentu ulotki z PDF dla każdego produktu
        for idx, product in enumerate(products, start=1):
            product_id = product["id"]
            nazwa = product["nazwaProduktu"]
            nazwa_powszechna = product["nazwaPowszechnieStosowana"]
            ulotka_url = product["ulotka"]

            # Pominięcie jeśli brak URL do ulotki
            if not ulotka_url or not ulotka_url.startswith("http"):
                print(f"[{idx}] Pomijam (brak poprawnej ulotki). Lek: {nazwa} ID: {product_id}")
                writer.writerow([product_id, nazwa, nazwa_powszechna, ""])
                continue

            # Pobranie opisu z ulotki
            analyzer = PdfUrlAnalyzer(ulotka_url)
            fragment = analyzer.get_fragment(start_marker, end_marker, min_length)
            if fragment:
                opis = fragment
                print(f"[{idx}] {nazwa} (ID: {product_id}) - Fragment pobrany ({len(opis)} znaków).")
            else:
                opis = ""
                print(f"[{idx}] Brak fragmentu w ulotce. Lek: {nazwa} (ID: {product_id}).")

            # Zapis do CSV
            writer.writerow([product_id, nazwa, nazwa_powszechna, opis])

    print(f"\nLista zapisana do pliku: {output_csv}")


if __name__ == "__main__":
    # Budowa listy leków z pliku XML
    xml_file = "resources/rejestr_produktow_leczniczych.xml"
    output_csv = "medications.csv"
    build_medication_list(xml_file, output_csv)
