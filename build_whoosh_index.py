# build_whoosh_index.py

import csv
import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import index


def build_index(csv_file, index_dir="indexdir"):
    """
    Tworzy indeks Whoosh na podstawie pliku CSV (medications.csv).

    Plik CSV powinien mieć nagłówki: id, nazwaProduktu, nazwaPowszechnieStosowana, opis.

    Parametry:
    - csv_file (str): ścieżka do pliku CSV.
    - index_dir (str): nazwa katalogu, w którym zostanie utworzony indeks Whoosh.
    """

    if not os.path.exists(csv_file):
        print(f"Brak pliku CSV: {csv_file}")
        return

    # Stworzenie folderu dla indeksu, jeśli nie istnieje
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    # Definicja schematu Whoosh
    # ID(stored=True) -> pole 'id' będzie identyfikatorem dokumentu
    # analyzer=StemmingAnalyzer() - stematyzacja słów, czyli ból i bólu będą traktowane tak samo
    schema = Schema(
        id=ID(stored=True, unique=True),
        nazwa=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        nazwaPowszechna=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        opis=TEXT(stored=True, analyzer=StemmingAnalyzer())
    )

    # Utwórz lub otwórz indeks
    # create_in -> tworzy nowy indeks w folderze, jeśli folder nie jest pusty, usunie stary
    idx = create_in(index_dir, schema=schema)

    writer = idx.writer()

    # Wczytujemy CSV i dodajemy dokumenty do indeksu
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        count = 0
        for row in reader:
            doc_id = row["id"]
            nazwa = row["nazwaProduktu"]
            nazwaPowszechna = row["nazwaPowszechnieStosowana"]
            opis = row["opis"]

            # Dodanie dokumentu do indeksu
            writer.add_document(
                id=doc_id,
                nazwa=nazwa,
                nazwaPowszechna=nazwaPowszechna,
                opis=opis
            )
            count += 1

    writer.commit()
    print(f"Zindeksowano {count} dokument(ów). Indeks zapisano w folderze: {index_dir}")


if __name__ == "__main__":
    CSV_FILE = "medications.csv"  # Plik źródłowy
    INDEX_DIR = "indexdir"  # Folder dla indeksu Whoosh

    build_index(CSV_FILE, INDEX_DIR)
