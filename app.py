import os
import math
from collections import defaultdict, Counter
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash

# Mengimpor komponen database dan fungsi pembantu dari file lain.
from models import db, Document, InvertedIndex, TermInfo
from read_file import extract_text_from_file, preprocess_text

# Membuat instance utama aplikasi Flask.
app = Flask(__name__)

# --- Konfigurasi Aplikasi ---
# Menyiapkan koneksi ke database, kunci rahasia untuk keamanan, dan folder untuk file.
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASS', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'db_search_engine')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'e2a1b3f4c5d6e7f8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4'
DATA_FOLDER = 'data_collection'
app.config['UPLOAD_FOLDER'] = DATA_FOLDER
os.makedirs(DATA_FOLDER, exist_ok=True)

# Menghubungkan objek database dengan aplikasi Flask.
db.init_app(app)

# --- Logika Inti Mesin Pencari ---

def perform_search(query_text):
    """Fungsi ini adalah 'otak' pencarian. Ia menerima kueri, menghitung skor TF-IDF,
    dan mengembalikan daftar dokumen yang sudah diurutkan berdasarkan relevansi."""
    
    if not query_text: return []
    # Membersihkan kueri pengguna (stemming, stopword).
    clean_query_terms = preprocess_text(query_text)
    if not clean_query_terms: return []

    print(f"Kueri bersih: {clean_query_terms}")

    total_documents = db.session.query(Document).count()
    if total_documents == 0: return []

    # Dictionary untuk menyimpan skor setiap dokumen.
    doc_scores = defaultdict(float)

    # Mengambil data TF (frekuensi kata) dan IDF (kelangkaan kata) dari database.
    term_infos = {info.term: info for info in TermInfo.query.filter(TermInfo.term.in_(clean_query_terms)).all()}
    index_entries = db.session.query(InvertedIndex).filter(InvertedIndex.term.in_(clean_query_terms)).all()

    # Menghitung skor TF-IDF untuk setiap dokumen yang relevan.
    for entry in index_entries:
        if entry.term in term_infos:
            tf = entry.frequency
            doc_count_with_term = term_infos[entry.term].doc_count
            idf = math.log(total_documents / (1 + doc_count_with_term))
            tf_idf_score = tf * idf
            doc_scores[entry.doc_id] += tf_idf_score

    if not doc_scores: return []
    
    # Mengurutkan dokumen berdasarkan skor tertinggi.
    sorted_doc_ids = sorted(doc_scores.keys(), key=lambda id: doc_scores[id], reverse=True)
    
    # Menyiapkan hasil akhir (objek dokumen + skornya) untuk ditampilkan.
    final_docs_map = {doc.id: doc for doc in Document.query.filter(Document.id.in_(sorted_doc_ids)).all()}
    
    results_with_scores = []
    for doc_id in sorted_doc_ids:
        if doc_id in final_docs_map:
            results_with_scores.append({
                'doc': final_docs_map[doc_id],
                'score': round(doc_scores[doc_id], 2)
            })
            
    return results_with_scores

# --- Routes Flask (URL Aplikasi) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Fungsi ini menangani halaman utama, baik saat pertama kali dibuka (GET)
    maupun saat pengguna mengirimkan formulir pencarian (POST)."""
    results = []
    query = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            # Memanggil fungsi 'otak' pencarian.
            results = perform_search(query)
            print(f"Hasil pencarian untuk '{query}': {len(results)} dokumen ditemukan")
    
    # Mengirimkan hasil ke file HTML untuk ditampilkan.
    return render_template('index.html', results=results, query=query)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Fungsi ini menangani proses unggah file baru. Ia tidak menampilkan halaman,
    hanya memproses file lalu mengarahkan pengguna kembali ke halaman utama."""
    
    # Validasi dasar untuk file yang diunggah.
    if 'file' not in request.files:
        flash("Request tidak valid: tidak ada bagian file.", "error")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash("Tidak ada file yang dipilih untuk diunggah.", "warning")
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        # Cek duplikat file.
        if Document.query.filter_by(filename=filename).first():
            flash(f"Dokumen '{filename}' sudah ada di database.", "warning")
            return redirect(url_for('index'))
        
        # Simpan file secara fisik.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Ekstrak teks mentah dari file.
        content_raw = extract_text_from_file(filepath)

        if content_raw:
            # Simpan konten mentah ke tabel 'Document'.
            new_doc = Document(filename=filename, content=content_raw)
            db.session.add(new_doc)
            db.session.flush()

            # Proses teks untuk diindeks.
            clean_terms = preprocess_text(content_raw)
            term_frequencies = Counter(clean_terms)

            # Simpan entri ke tabel 'InvertedIndex' (info TF).
            for term, frequency in term_frequencies.items():
                new_index_entry = InvertedIndex(term=term, doc_id=new_doc.id, frequency=frequency)
                db.session.add(new_index_entry)

            # Perbarui tabel 'TermInfo' (info IDF).
            unique_terms_in_doc = set(clean_terms)
            for term in unique_terms_in_doc:
                term_info = TermInfo.query.filter_by(term=term).first()
                if term_info:
                    term_info.doc_count += 1
                else:
                    new_term_info = TermInfo(term=term, doc_count=1)
                    db.session.add(new_term_info)
            
            # Simpan semua perubahan ke database.
            db.session.commit()
            flash(f"File '{filename}' berhasil diunggah dan diindeks dengan benar!", "success")
        else:
            flash(f"Gagal mengekstrak teks dari '{filename}'.", "error")

        # Arahkan pengguna kembali ke halaman utama.
        return redirect(url_for('index'))

    return redirect(url_for('index'))


# --- Menjalankan PRogram ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)