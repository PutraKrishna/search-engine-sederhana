import os
import math
from collections import defaultdict, Counter
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash

# Impor dari file-file baru kita
from models import db, Document, InvertedIndex, TermInfo
from read_file import extract_text_from_file, preprocess_text

app = Flask(__name__)

# --- KONFIGURASI ---
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASS', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'db_search_engine')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ganti-dengan-kunci-rahasia-yang-benar-benar-acak'

# Gunakan nama folder yang konsisten
DATA_FOLDER = 'data_collection'
app.config['UPLOAD_FOLDER'] = DATA_FOLDER
os.makedirs(DATA_FOLDER, exist_ok=True)
# --------------------

# Hubungkan 'db' dari models.py dengan 'app' kita
db.init_app(app)

# --- LOGIKA INTI PENCARIAN ---

def perform_search(query_text):
    if not query_text: return []
    clean_query_terms = preprocess_text(query_text)
    if not clean_query_terms: return []

    print(f"Kueri bersih: {clean_query_terms}")

    total_documents = db.session.query(Document).count()
    if total_documents == 0: return []

    doc_scores = defaultdict(float) # Gunakan float karena skor TF-IDF adalah desimal

    # Ambil semua informasi term (IDF) yang relevan dalam satu query
    term_infos = {info.term: info for info in TermInfo.query.filter(TermInfo.term.in_(clean_query_terms)).all()}

    # Ambil semua entri indeks (TF) yang relevan dalam satu query
    index_entries = db.session.query(InvertedIndex).filter(InvertedIndex.term.in_(clean_query_terms)).all()

    # Hitung skor TF-IDF untuk setiap dokumen
    for entry in index_entries:
        if entry.term in term_infos:
            # TF (Term Frequency)
            tf = entry.frequency
            # IDF (Inverse Document Frequency)
            doc_count_with_term = term_infos[entry.term].doc_count
            idf = math.log(total_documents / (1 + doc_count_with_term)) # +1 untuk menghindari pembagian dengan nol
            
            tf_idf_score = tf * idf
            doc_scores[entry.doc_id] += tf_idf_score

    if not doc_scores: return []
    
    # Urutkan dokumen berdasarkan skor TF-IDF tertinggi
    sorted_doc_ids = sorted(doc_scores.keys(), key=lambda id: doc_scores[id], reverse=True)
    
    # Ambil objek dokumen dan siapkan hasil akhir dengan skornya
    final_docs_map = {doc.id: doc for doc in Document.query.filter(Document.id.in_(sorted_doc_ids)).all()}
    
    results_with_scores = []
    for doc_id in sorted_doc_ids:
        if doc_id in final_docs_map:
            results_with_scores.append({
                'doc': final_docs_map[doc_id],
                'score': round(doc_scores[doc_id], 2) # Bulatkan skor agar lebih rapi
            })
            
    return results_with_scores

# --- ROUTES FLASK ---

# ✅ ROUTE UTAMA - INI YANG KURANG!
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            results = perform_search(query)
            print(f"Hasil pencarian untuk '{query}': {len(results)} dokumen ditemukan")
    
    return render_template('index.html', results=results, query=query)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("Request tidak valid: tidak ada bagian file.", "error")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash("Tidak ada file yang dipilih untuk diunggah.", "warning")
        return redirect(url_for('index'))
    if file:
        filename = secure_filename(file.filename)
        if Document.query.filter_by(filename=filename).first():
            flash(f"Dokumen '{filename}' sudah ada di database.", "warning")
            return redirect(url_for('index'))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        content_raw = extract_text_from_file(filepath)
        if content_raw:
            new_doc = Document(filename=filename, content=content_raw)
            db.session.add(new_doc)
            db.session.flush()
            clean_terms = preprocess_text(content_raw)
            term_frequencies = Counter(clean_terms)
            for term, frequency in term_frequencies.items():
                new_index_entry = InvertedIndex(term=term, doc_id=new_doc.id, frequency=frequency)
                db.session.add(new_index_entry)
            unique_terms_in_doc = set(clean_terms)
            for term in unique_terms_in_doc:
                term_info = TermInfo.query.filter_by(term=term).first()
                if term_info:
                    term_info.doc_count += 1
                else:
                    new_term_info = TermInfo(term=term, doc_count=1)
                    db.session.add(new_term_info)
            db.session.commit()
            flash(f"File '{filename}' berhasil diunggah dan diindeks dengan benar!", "success")
        else:
            flash(f"Gagal mengekstrak teks dari '{filename}'.", "error")
        return redirect(url_for('index'))
    return redirect(url_for('index'))
# -------------------

if __name__ == '__main__':
    with app.app_context():
        # Membuat tabel jika belum ada
        db.create_all()
    app.run(debug=True, port=5001)