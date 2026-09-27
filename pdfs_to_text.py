#%%

from pypdf import PdfReader
from backend.constants import DATA_PATH

def extract_text_from_pdf(path) -> str:
    
    reader = PdfReader(path)

    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

        return all_text               

def export_text_to_txt(text, path):
    # Προσθήκη encoding='utf-8' μέσα στο open()
    # για αποτροπή κρασαρίσματος σε Windows, καθώς η προεπιλογή (cp1252) # δεν αναγνωρίζει ειδικά σύμβολα ή emoji των PDF.
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)

if __name__ == "__main__":
   for pdf_path in DATA_PATH.glob("*.pdf"):
       pdf_text = extract_text_from_pdf(pdf_path)

       filename = f"{pdf_path.stem.casefold()}.txt"

       export_text_to_txt(pdf_text, DATA_PATH/ filename)


#%%