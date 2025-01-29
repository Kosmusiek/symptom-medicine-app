import os
import sys
import requests
import PySimpleGUI as sg

from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh import scoring

from rejestr_produktow_leczniczych_parser import RejestrProduktowLeczniczychParser

sg.set_options(font=("Aptos", 12))

def do_search(query_str, limit, sort_order, idx):
    """
    Wykonuje wyszukiwanie w indeksie Whoosh, zwraca listę słowników.

    Parametry:
    - query_str (str): Zapytanie od użytkownika (np. objawy, słowa kluczowe).
    - limit (int): Maksymalna liczba wyników do pobrania.
    - sort_order (str): Metoda sortowania ("Score" lub "Alfabetycznie").
    - idx (whoosh.index.Index): Otwarty indeks Whoosh (open_dir).

    Zwraca:
    - list[dict]: Lista słowników z polami, np.:
      [
        {
          "id": "...",
          "nazwa": "...",
          "nazwaPowszechna": "...",
          "opis": "...",
          "pdf_url": "...",
          "score": 2.3456
        },
        ...
      ]
      Każdy słownik reprezentuje jeden dokument w indeksie.
    """

    if not query_str:
        return []

    parser = MultifieldParser(["nazwa", "nazwaPowszechna", "opis"], schema=idx.schema, group=OrGroup)
    search_query = parser.parse(query_str)

    final_results = []
    with idx.searcher(weighting=scoring.BM25F()) as searcher:
        results = searcher.search(search_query, limit=limit)
        for r in results:
            # Konwersja obiektu wyniku (Hit) do słownika
            doc_fields = dict(r.fields())
            doc_fields["score"] = r.score
            final_results.append(doc_fields)

    # Ewentualne sortowanie alfabetyczne po polu "nazwa"
    if sort_order == "Alfabetycznie":
        final_results.sort(key=lambda x: x.get("nazwa", "").lower())

    return final_results

def build_table_values(final_results):
    """
    Przygotowuje dane do wyświetlenia w tabeli PySimpleGUI (sg.Table).

    Parametry:
    - final_results (list[dict]): Lista słowników zwrócona przez do_search().

    Zwraca:
    - list[list[str]]: Dane wierszy do przekazania do elementu sg.Table,
      np. [
        ["1001", "Aspiryna", "Acidum acetylsalicylicum", "2.3456"],
        ...
      ]
    """

    table_data = []
    for doc in final_results:
        doc_id = doc.get("id", "")
        nazwa = doc.get("nazwa", "")
        nazwa_p = doc.get("nazwaPowszechna", "")
        score = f"{doc.get('score', 0):.4f}"

        row = [doc_id, nazwa, nazwa_p, score]
        table_data.append(row)

    return table_data

def medicine_explorer_app():
    """
    Główna funkcja aplikacji GUI do przeglądania i pobierania informacji o lekach.

    - Ładuje parser XML (rejestr_produktow_leczniczych_parser.py) z pliku:
      'resources/rejestr_produktow_leczniczych.xml'.
    - Otwiera indeks Whoosh w katalogu 'indexdir'.
    - Pozwala wyszukać leki wg słów kluczowych i ustalić liczbę wyników oraz metodę sortowania.
    - Wyświetla wyniki w tabeli:
      [ID, Nazwa, Nazwa powsz., Score]
    - Przyciski:
      * "Wyświetl opis" – pokazuje pełen opis z indeksu Whoosh.
      * "Wyświetl więcej informacji" – wywołuje parser.get_info(id) i wyświetla szczegóły.
      * "Pobierz ulotkę" i "Pobierz charakterystykę" – pobiera pliki PDF z adresów określonych w pliku XML,
        zapisywane w folderze "downloads".

    Zwraca:
    - None

    Zakończenie następuje po wybraniu "Wyjście" lub zamknięciu okna.
    """

    parser = RejestrProduktowLeczniczychParser("resources/rejestr_produktow_leczniczych.xml")

    index_dir = "indexdir"
    if not os.path.exists(index_dir):
        sg.popup_error(f"Nie znaleziono katalogu indeksu: {index_dir}")
        sys.exit(1)

    try:
        idx = open_dir(index_dir)
    except:
        sg.popup_error(f"Nie można otworzyć indeksu w folderze: {index_dir}")
        sys.exit(1)

    # Folder do pobierania plików PDF
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.mkdir(download_folder)

    # Layout parametrów wyszukiwania
    layout_search = [
        [sg.Text("Zapytanie:", size=(12,1)), sg.Input(key="-QUERY-", size=(40,1))],
        [sg.Text("Liczba wyników:", size=(12,1)),
         sg.Spin([i for i in range(1,101)], initial_value=10, key="-LIMIT-")],
        [sg.Text("Sortowanie:", size=(12,1)),
         sg.Combo(["Score", "Alfabetycznie"], default_value="Score", key="-SORT-", size=(20,1))],
        [sg.Button("Szukaj", bind_return_key=True), sg.Button("Wyjście")]
    ]

    # Nagłówki i tabela
    headings = ["ID", "Nazwa", "Nazwa powsz.", "Score"]
    layout_table = [
        [sg.Table(
            values=[],
            headings=headings,
            key="-TABLE-",
            enable_events=True,
            auto_size_columns=True,
            justification="left",
            num_rows=15,
            expand_x=True
        )]
    ]

    # Przyciski operacyjne
    layout_bottom = [
        [sg.Button("Wyświetl opis", key="-SHOWDESC-"),
         sg.Button("Wyświetl więcej informacji", key="-SHOWINFO-"),
         sg.Button("Pobierz ulotkę", key="-GETULOTKA-"),
         sg.Button("Pobierz charakterystykę", key="-GETCHAR-")]
    ]

    # Kompletny layout
    layout = [
        [sg.Frame("Parametry wyszukiwania", layout_search, pad=(10,10), expand_x=True)],
        [sg.Frame("Wyniki wyszukiwania", layout_table, pad=(10,10), expand_x=True)],
        [sg.Frame("Operacje", layout_bottom, pad=(10,10), expand_x=True)]
    ]

    # Okno PySimpleGUI
    window = sg.Window("Przeglądarka leków (symptom-medicine-app)", layout, resizable=True, size=(1000,600))

    cached_results = []

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Wyjście"):
            break

        if event == "Szukaj":
            query_str = values["-QUERY-"].strip()
            limit = int(values["-LIMIT-"])
            sort_order = values["-SORT-"]

            final_results = do_search(query_str, limit, sort_order, idx)
            cached_results = final_results

            table_data = build_table_values(final_results)
            window["-TABLE-"].update(values=table_data)

            if not final_results:
                sg.popup("Brak wyników.")

        if event in ("-SHOWDESC-", "-SHOWINFO-", "-GETULOTKA-", "-GETCHAR-"):
            selected = values["-TABLE-"]
            if not selected:
                sg.popup_error("Nie wybrano żadnego wiersza.")
                continue

            row_index = selected[0]
            doc = cached_results[row_index]  # Słownik zwrócony przez do_search
            doc_id = doc.get("id", "")

            if event == "-SHOWDESC-":
                # Wyświetlenie pełnego opisu z indeksu
                full_opis = doc.get("opis", "").strip()  # Usuń nadmiarowe spacje i nowe linie
                lines = full_opis.split("\n")  # Podziel tekst na linie
                if len(lines) > 1:
                    full_opis = "\n".join(lines[:-1])  # Połącz ponownie bez ostatniej linii

                sg.popup_scrolled(full_opis, title=f"Pełny opis - ID={doc_id}")

            elif event == "-SHOWINFO-":
                # Pobranie szczegółowych informacji z pliku XML
                info_dict = parser.get_info(doc_id)
                if not info_dict:
                    sg.popup_error(f"Nie znaleziono info o produkcie ID={doc_id} w pliku XML.")
                else:
                    lines = []
                    for k, v in info_dict.items():
                        if k == "kodyATC":
                            # v to lista, np. ["M05BA08"]
                            lines.append(f"{k}: {', '.join(v)}")
                        else:
                            lines.append(f"{k}: {v}")
                    info_text = "\n".join(lines)
                    sg.popup_scrolled(info_text, title=f"Szczegółowe informacje o leku - ID={doc_id}")

            elif event == "-GETULOTKA-":
                ulotka_url, _ = parser.get_url(doc_id)
                if not ulotka_url.startswith("http"):
                    sg.popup_error("Brak poprawnego adresu (ulotka) w XML.")
                    continue
                try:
                    r = requests.get(ulotka_url, timeout=10)
                    r.raise_for_status()
                    filename = os.path.join(download_folder, f"ulotka_{doc_id}.pdf")
                    with open(filename, "wb") as f_pdf:
                        f_pdf.write(r.content)
                    sg.popup(f"Pobrano ulotkę: {filename}")
                except Exception as e:
                    sg.popup_error(f"Błąd pobierania ulotki: {e}")

            elif event == "-GETCHAR-":
                _, char_url = parser.get_url(doc_id)
                if not char_url.startswith("http"):
                    sg.popup_error("Brak poprawnego adresu (charakterystyka) w XML.")
                    continue
                try:
                    r = requests.get(char_url, timeout=10)
                    r.raise_for_status()
                    filename = os.path.join(download_folder, f"charakterystyka_{doc_id}.pdf")
                    with open(filename, "wb") as f_pdf:
                        f_pdf.write(r.content)
                    sg.popup(f"Pobrano charakterystykę: {filename}")
                except Exception as e:
                    sg.popup_error(f"Błąd pobierania charakterystyki: {e}")

    window.close()

if __name__ == "__main__":
    medicine_explorer_app()
