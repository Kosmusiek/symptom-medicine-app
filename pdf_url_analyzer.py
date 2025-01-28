# pdf_url_analyzer.py

import requests
import pymupdf

class PdfUrlAnalyzer:
    """
    Klasa umożliwia pobranie pliku PDF z podanego adresu URL i wyodrębnienie
    tekstu. Daje również opcję wyszukiwania fragmentu między znacznikami.
    """

    def __init__(self, url):
        """
        Inicjalizuje obiekt klasy PdfUrlAnalyzer, przechowując adres URL
        pliku PDF, który ma zostać pobrany i przeanalizowany.

        Parametry:
        - url (str): Adres URL wskazujący na plik PDF do pobrania.
        """
        self.url = url
        self.full_text = None  # Zmienna, w której przechowamy wyodrębniony tekst PDF

    def get_text(self):
        """
        Pobiera plik PDF z zadanego adresu URL, wyodrębnia cały tekst i zapamiętuje
        go w zmiennej self.full_text.

        Obsługiwane błędy:
        - requests.exceptions.RequestException: błędy związane z pobieraniem pliku.
        - ValueError: błędy związane z niepoprawnymi indeksami.

        Zwraca:
        - str: pełny tekst wyodrębniony z PDF (lub None, jeśli wystąpił błąd).
        """
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # Zgłasza błąd, jeśli status != 200
            pdf_bytes = response.content

            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            extracted_text = []
            for page in doc:
                extracted_text.append(page.get_text())

            self.full_text = "".join(extracted_text)
            return self.full_text

        except requests.exceptions.RequestException as e:
            print(f"[PdfUrlAnalyzer] Błąd pobierania pliku PDF: {e}")
            return None
        except Exception as e:
            print(f"[PdfUrlAnalyzer] Nieoczekiwany błąd: {e}")
            return None

    def get_fragment(self, start_marker, end_marker, min_length=50):
        """
        Zwraca fragment tekstu zawarty między start_marker i end_marker.
        Jeśli self.full_text jest puste (None), wywołuje fetch_pdf_content, aby wczytać tekst.

        Jeśli odnaleziony fragment będzie krótszy niż min_length, metoda spróbuje znaleźć
        kolejne wystąpienie start_marker (o ile istnieje). W przypadku, gdy nie uda się
        znaleźć wystarczająco długiego fragmentu, metoda zwraca None.

        Parametry:
        - start_marker (str): tekst wyznaczający początek fragmentu.
        - end_marker (str): tekst wyznaczający koniec fragmentu.
        - min_length (int): minimalna długość odnalezionego fragmentu,
          domyślnie 50.

        Zwraca:
        - str: wyodrębniony fragment, jeśli został znaleziony wystarczająco długi,
               w przeciwnym razie None.
        """
        # Jeśli nie pobrano jeszcze tekstu, pobierz go
        if self.full_text is None:
            self.get_text()

        if not self.full_text:
            # Jeśli po próbie pobrania dalej nie ma tekstu,
            # kończymy z None.
            return None

        # Jeśli nie podano markerów, zwróć cały tekst
        if not start_marker or not end_marker:
            return self.full_text

        search_position = 0
        while True:
            start_index = self.full_text.find(start_marker, search_position)
            if start_index == -1:
                return None

            end_index = self.full_text.find(end_marker, start_index + len(start_marker))
            if end_index == -1:
                return None

            fragment_length = end_index - (start_index + len(start_marker))
            if fragment_length >= min_length:
                fragment_text = self.full_text[start_index + len(start_marker) : end_index]
                return fragment_text.strip()
            else:
                # Szukaj kolejnego wystąpienia start_marker
                search_position = start_index + len(start_marker)
