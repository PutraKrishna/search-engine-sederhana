import os
from collections import Counter

# Impor semua komponen yang dibutuhkan dari file-file yang sudah dipisah
from app import app
# --- PERUBAHAN 1: Impor model TermInfo yang baru ---
from models import db, Document, InvertedIndex, TermInfo
from read_file import extract_text_from_file, preprocess_text

def populate_database():
    """
    Membaca file, menghitung TF dan IDF, dan menyimpannya ke database.
    Ini adalah proses dua langkah.
    """
    print("Memulai proses pengisian database untuk TF-IDF...")
    data_folder = 'data_collection'
    
    # --- PERUBAHAN 2: Hapus data lama untuk memastikan konsistensi ---
    # Best Practice: Selalu bersihkan data lama saat logika indexing berubah.
    print("Membersihkan data lama dari tabel...")
    TermInfo.query.delete()
    InvertedIndex.query.delete()
    Document.query.delete()
    db.session.commit()
    # -------------------------------------------------------------

    # --- LANGKAH 1: KUMPULKAN INFORMASI DARI SEMUA DOKUMEN ---
    all_docs_terms = {} # Kamus sementara untuk menyimpan {doc_id: [list_of_terms]}
    total_docs = 0
    
    print("Langkah 1: Membaca dan memproses semua dokumen...")
    filenames = os.listdir(data_folder)
    for filename in filenames:
        filepath = os.path.join(data_folder, filename)
        content_raw = extract_text_from_file(filepath)
        
        if content_raw:
            total_docs += 1
            
            # Simpan dokumen mentah
            new_doc = Document(filename=filename, content=content_raw)
            db.session.add(new_doc)
            db.session.flush() # Dapatkan ID untuk new_doc

            # Proses teks dan simpan hasilnya di kamus sementara
            clean_terms = preprocess_text(content_raw)
            all_docs_terms[new_doc.id] = clean_terms
    # -----------------------------------------------------------

    # --- LANGKAH 2: HITUNG IDF, LALU SIMPAN SEMUANYA ---
    print("Langkah 2: Menghitung IDF dan menyimpan data ke database...")

    # A. Hitung Document Frequency (di berapa banyak dokumen sebuah term muncul)
    term_doc_counts = Counter()
    for doc_id, terms in all_docs_terms.items():
        unique_terms_in_doc = set(terms)
        for term in unique_terms_in_doc:
            term_doc_counts[term] += 1
            
    # B. Simpan informasi ini ke tabel TermInfo ("Kamus Popularitas")
    for term, count in term_doc_counts.items():
        term_info = TermInfo(term=term, doc_count=count)
        db.session.add(term_info)
        
    # C. Sekarang, buat InvertedIndex dengan frekuensi (TF)
    for doc_id, terms in all_docs_terms.items():
        term_frequencies = Counter(terms) # Menghitung TF
        for term, freq in term_frequencies.items():
            index_entry = InvertedIndex(term=term, doc_id=doc_id, frequency=freq)
            db.session.add(index_entry)

    # D. Commit semua perubahan sekaligus
    try:
        print("Menyimpan semua data ke database...")
        db.session.commit()
        print("Proses pengisian database dengan data TF-IDF selesai!")
    except Exception as e:
        print(f"Terjadi error saat commit! Membatalkan perubahan: {e}")
        db.session.rollback()
    # -----------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        populate_database()