#Autor: Kosma Skajewski

import requests
from io import BytesIO
from PyPDF2 import PdfReader


def fetch_pdf_content(url, start_marker=None, end_marker=None, min_length=50):
    """
    Funkcja pobiera plik PDF ze wskazanego adresu URL, wyodrębnia cały tekst i zwraca go.

    Jeśli jednocześnie podane zostaną argumenty start_marker i end_marker, to funkcja
    będzie dodatkowo próbowała znaleźć fragment między tymi znacznikami. Jeśli
    odnaleziony fragment będzie krótszy niż min_length, funkcja spróbuje znaleźć
    kolejne wystąpienie start_marker (o ile istnieje). W przypadku, gdy nie uda się
    znaleźć wystarczająco długiego fragmentu, funkcja zwraca None.

    Parametry:
    - url (str): adres URL wskazujący na plik PDF do pobrania.
    - start_marker (str, opcjonalnie): tekst wyznaczający początek fragmentu.
    - end_marker (str, opcjonalnie): tekst wyznaczający koniec fragmentu.
    - min_length (int, opcjonalnie): minimalna długość odnalezionego fragmentu, domyślnie 50.

    Zwraca:
    - str: cały tekst (jeśli nie podano obu znaczników) lub wyodrębniony fragment,
      jeśli został znaleziony wystarczająco długi. W przeciwnym razie None.
    """
    # PDF zapisany w formie bajtów (pdf_bytes)
    response = requests.get(url)
    pdf_bytes = BytesIO(response.content)

    # Odczytanie pliku PDF za pomocą PyPDF2
    pdf_reader = PdfReader(pdf_bytes)

    # Tekst ze wszystkich stron
    pages_text = map(lambda page: page.extract_text(), pdf_reader.pages)

    # Połączenie tekstu ze wszystkich stron w jeden string
    full_text = " ".join(pages_text)

    # Jeśli nie ma zdefiniowanych znaczników, zwróć cały tekst
    if not start_marker or not end_marker:
        return full_text

    # W przeciwnym razie spróbuj znaleźć fragment między znacznikami
    search_position = 0
    while True:
        # Znajdź start_marker od pozycji search_position
        start_index = full_text.find(start_marker, search_position)
        if start_index == -1: # Nie znaleziono  start_marker
            return None

        # Znajdź end_marker od miejsca tuż za znalezionym start_marker
        end_index = full_text.find(end_marker, start_index + len(start_marker))
        if end_index == -1: # Nie znaleziono end_marker
            return None

        fragment_length = end_index - (start_index + len(start_marker))

        if fragment_length >= min_length:
            full_text = full_text[start_index + len(start_marker): end_index]
            return full_text.strip()
        else:
            # Szukaj kolejnego wystąpienia start_marker
            search_position = start_index + len(start_marker)

# Przykładowe użycie funkcji
def main():
    # Ulotka leku z Rejestru Produktów Leczniczych (rejestry.ezdrowie.gov.pl)
    url = "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/225/leaflet"

    start = "i w jakim celu się go stosuje"
    end = "2. Informacje ważne przed"
    fragment_text = fetch_pdf_content(url, start, end, min_length=50)

    if fragment_text:
        print("Znaleziony fragment:\n", fragment_text)
    else:
        print("Nie znaleziono wystarczająco długiego fragmentu między znacznikami.")


if __name__ == "__main__":
    main()
