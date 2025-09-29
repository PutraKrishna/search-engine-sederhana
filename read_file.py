import os
import PyPDF2
import docx
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.StopWordRemover.StopWordRemover import StopWordRemover
from Sastrawi.Dictionary.ArrayDictionary import ArrayDictionary

# --- Inisialisasi Sastrawi hanya terjadi di satu tempat ini ---
print("Menginisialisasi Sastrawi...")
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stopword_factory = StopWordRemoverFactory()
default_stopwords = stopword_factory.get_stop_words()
exceptions = ["bitcoin"]
custom_stopwords = [word for word in default_stopwords if word not in exceptions]
custom_dictionary = ArrayDictionary(custom_stopwords)
stopword_remover = StopWordRemover(custom_dictionary)
print("Sastrawi siap digunakan.")
# -----------------------------------------------------------

def extract_text_from_file(filepath):
    """Mengekstrak teks mentah dari file .pdf, .docx, dan .txt."""
    text = ""
    try:
        if filepath.endswith('.pdf'):
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text: text += page_text + "\n"
        elif filepath.endswith('.docx'):
            doc = docx.Document(filepath)
            for para in doc.paragraphs: text += para.text + "\n"
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as file: text = file.read()
    except Exception as e:
        print(f"Error saat mengekstrak file {os.path.basename(filepath)}: {e}")
        return None
    return text

def preprocess_text(text):
    """Memproses teks mentah menjadi daftar kata kunci bersih."""
    text = text.lower()
    text_without_stopwords = stopword_remover.remove(text)
    stemmed_text = stemmer.stem(text_without_stopwords)
    stemmed_tokens = stemmed_text.split()
    final_tokens = [t for t in stemmed_tokens if t.isalpha()]
    return final_tokens