# Symptom Medicine App


**PL**

**Symptom Medicine App** to aplikacja GUI oparta na Pythonie, umożliwiająca użytkownikom wyszukiwanie leków na podstawie objawów. Aplikacja jest przystosowana do wyszukiwania produktów z **Rejestru Produktów Leczniczych Dopuszczonych do Obrotu na terytorium Rzeczypospolitej Polskiej**. Pobiera istotne informacje z ulotek leków i dostarcza szczegółowe opisy, w tym możliwość pobrania oficjalnych ulotek i charakterystyki produktów leczniczych.


---

**ENG**

**Symptom Medicine App** is a Python-based GUI application that allows users to search for medicines based on their symptoms. The application is designed to search for products listed in the **Register of Medicinal Products Authorized for Marketing in the Territory of the Republic of Poland**. It extracts relevant information from medicine leaflets and provides detailed descriptions, including the option to download official leaflets and product characteristics.

## Features

- **Search for medicines** based on symptoms or keywords.
- **Display detailed information** about the medicine, including its active substances, dosage, and legal information.
- **Download** the official leaflet (`ulotka`) and product characteristics (`charakterystyka`) as PDFs.
- **Sort results** by relevance (score) or alphabetically.

## Requirements

Before running the application, make sure you have the following installed:

- **Python 3.8 or later**
- **Required Python libraries** – install them using:

  ```bash
  pip install requests pymupdf whoosh PySimpleGUI


## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Kosmusiek/symptom-medicine-app.git
   cd symptom-medicine-app

2. **Download the latest medicine registry XML file**:
- Go to: [Rejestr Produktów Leczniczych](https://rejestry.ezdrowie.gov.pl/registry/rpl)
- In the section **"Aktualny rejestr produktów leczniczych"**, locate:
  - **Rejestr produktów leczniczych - stan na dzień podany w nazwie pliku - całościowy**
- Download the **XML file** (`Rejestr_Produktow_Leczniczych_calosciowy_stan_na_dzien_<date>_<version>.xml`).
- Place the file inside the **`resources/`** directory:
  symptom-medicine-app/resources/

3. **Build the medicine database from XML**:
    ```bash
    python build_medication_list.py

5. **Build a Whoosh search index**:
    ```bash
    python build_whoosh_index.py

4. **Run the application**:
   ```bash
   python medicine_explorer.py

## Usage

- Enter **keywords** describing symptoms (e.g., `"ból pleców i mięśni, gorączka"`).
- Set the **number of results** to display.
- Choose **sorting method**: **by relevance** (score) or **alphabetically**.
- Click **"Search"** to retrieve medicines related to the symptoms.
- Click **"Show More Information"** to see additional details.
- Use **"Download Leaflet"** or **"Download Characteristics"** to save PDFs.

## Notes

- The application requires an updated version of the **medicine registry XML file** to function correctly.
- All downloaded PDFs are stored in the `downloads/` folder.

## License

This project is under the **MIT License**.





