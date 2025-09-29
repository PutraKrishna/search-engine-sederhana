import os
from collections import Counter

# Impor semua komponen yang dibutuhkan dari file-file yang sudah dipisah
from app import app
from models import db, Document, InvertedIndex
from read_file import extract_text_from_file, preprocess_text

def populate_database():
    """Membaca file dari folder data, memproses, dan menyimpannya ke database."""
    # Pastikan nama folder konsisten
    data_folder = 'koleksi_data'
    
    try:
        filenames = os.listdir(data_folder)
        print(f"Menemukan {len(filenames)} file untuk diproses.")
        
        for i, filename in enumerate(filenames):
            filepath = os.path.join(data_folder, filename)

            if Document.query.filter_by(filename=filename).first():
                print(f"({i+1}/{len(filenames)}) Dokumen {filename} sudah ada, dilewati.")
                continue

            print(f"({i+1}/{len(filenames)}) Memproses {filename}...")
            content_raw = extract_text_from_file(filepath)
            
            if not content_raw:
                print(f"Gagal mengekstrak teks dari {filename}, dilewati.")
                continue
            
            # Simpan dokumen mentah
            new_doc = Document(filename=filename, content=content_raw)
            db.session.add(new_doc)
            db.session.flush() # Dapatkan ID untuk new_doc

            # Proses dan simpan ke inverted index
            clean_terms = preprocess_text(content_raw)
            term_frequencies = Counter(clean_terms)
            for term, frequency in term_frequencies.items():
                new_index_entry = InvertedIndex(term=term, doc_id=new_doc.id, frequency=frequency)
                db.session.add(new_index_entry)

        print("\nMenyimpan semua perubahan ke database...")
        db.session.commit()
        print("Proses pengisian database selesai!")

    except Exception as e:
        print(f"\nTerjadi error! Membatalkan perubahan: {e}")
        db.session.rollback()

if __name__ == '__main__':
    # Jalankan fungsi di dalam konteks aplikasi Flask
    with app.app_context():
        populate_database()