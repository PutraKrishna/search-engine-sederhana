from flask_sqlalchemy import SQLAlchemy

# Inisialisasi objek db di sini, tanpa aplikasi.
# Ini adalah kunci untuk menghindari circular import.
db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    filename = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)

class InvertedIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False, index=True) 
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
