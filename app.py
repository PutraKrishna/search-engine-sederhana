import os
from collections import defaultdict, Counter
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash

# Impor dari file-file baru kita
from models import db, Document, InvertedIndex
from read_file import extract_text_from_file, preprocess_text

app = Flask(__name__)

# --- KONFIGURASI ---
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASS', '123')
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

    doc_scores = defaultdict(int)
    index_entries = db.session.query(InvertedIndex.doc_id, InvertedIndex.frequency).filter(
        InvertedIndex.term.in_(clean_query_terms)).all()

    for doc_id, frequency in index_entries:
        doc_scores[doc_id] += frequency

    if not doc_scores: return []

    sorted_doc_ids = sorted(doc_scores.keys(), key=lambda id: doc_scores[id], reverse=True)
    
    final_docs_map = {doc.id: doc for doc in Document.query.filter(Document.id.in_(sorted_doc_ids)).all()}
    final_results = [final_docs_map[doc_id] for doc_id in sorted_doc_ids if doc_id in final_docs_map]
    
    return final_results
# ---------------------------

# --- ROUTES FLASK ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query_text = request.form.get('query', '')
        results = perform_search(query_text)
        return render_template('index.html', results=results, query=query_text)
    return render_template('index.html', results=[], query='')

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
            
            db.session.commit()
            flash(f"File '{filename}' berhasil diunggah dan diindeks!", "success")
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

