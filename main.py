import requests
from io import BytesIO
from PyPDF2 import PdfReader

# Funkcja pobierająca PDF z podanego URL
def fetch_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200: # 200 - OK
        return BytesIO(response.content)
    else:
        raise Exception(f"Nie udało się pobrać PDF-a. Kod odpowiedzi: {response.status_code}")

# Funkcja odczytująca treść PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Przykład użycia
url = "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/225/leaflet"
try:
    pdf_file = fetch_pdf_from_url(url)
    pdf_text = extract_text_from_pdf(pdf_file)
    print("Treść PDF-a:")
    print(pdf_text)
except Exception as e:
    print(f"Wystąpił błąd: {e}")
