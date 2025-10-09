# 🔍 TokenVerse - Search Egnien Sederhana

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Sebuah sistem *information retrieval* (mesin pencari) yang dibangun dengan Python & Flask. Sistem ini mampu mengindeks koleksi dokumen digital (.txt, .pdf, .docx) dan melakukan pencarian berdasarkan relevansi menggunakan algoritma ranking TF-IDF dengan dukungan pemrosesan bahasa Indonesia.

---

## ✨ Fitur Utama

- **🎯 Ranking Cerdas (TF-IDF)** - Algoritma *Term Frequency-Inverse Document Frequency* untuk menghasilkan hasil pencarian yang relevan
- **📁 Dukungan Multi-Format** - Mendukung dokumen dalam format .txt, .pdf, dan .docx
- **🇮🇩 Pemrosesan Teks Bahasa Indonesia** - Menggunakan Sastrawi untuk stemming dan stopword removal
- **💻 Antarmuka Pengguna Interaktif** - UI modern dan responsif dengan Tailwind CSS
- **📤 Manajemen Data Dinamis** - Fitur upload dokumen langsung dari interface
- **💾 Penyimpanan Persisten** - Database MySQL untuk menyimpan dokumen dan hasil preprocessing

---

## 🛠️ Tumpukan Teknologi

| Komponen | Teknologi |
|:---------|:----------|
| **Backend** | Python, Flask |
| **Frontend** | HTML, Tailwind CSS |
| **Database** | MySQL |
| **ORM** | Flask-SQLAlchemy |
| **NLP** | Sastrawi |
| **File Processing** | PyPDF2, python-docx |

---

## 📂 Struktur Proyek

```
tokenverse/
├── app.py                 # Pusat kendali aplikasi web (Flask routes)
├── models.py              # Definisi tabel database (SQLAlchemy models)
├── read_file.py           # Fungsi pembantu (ekstraksi, preprocessing, TF-IDF)
├── populate_db.py         # Skrip untuk mengisi data awal ke database
├── requirements.txt       # Daftar dependensi Python
├── package.json           # Konfigurasi Node.js untuk Tailwind CSS
├── tailwind.config.js     # Konfigurasi Tailwind CSS
├── templates/             # Folder berisi file HTML
│   ├── index.html         # Halaman utama aplikasi
├── static/                # Folder untuk file statis (CSS, JS, images)
│   └── css/
│       └── output.css     # File CSS hasil kompilasi Tailwind
└── data_collection/       # Folder untuk menyimpan dokumen yang diupload
```

---

## 🚀 Cara Instalasi dan Menjalankan

### Prasyarat

Pastikan Anda sudah menginstal:
- Python 3.8 atau lebih tinggi
- Node.js dan npm
- MySQL Server

### 1️⃣ Clone Repositori

```bash
git clone https://github.com/PutraKrishna/search_engine_sederhana.git
cd search_engine_sederhana
```

### 2️⃣ Setup Backend (Python)

**Buat dan aktifkan virtual environment:**

```bash
# Untuk Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Untuk Windows
python -m venv venv
venv\Scripts\activate
```

**Install Library yang dibutuhkan:**

```bash
pip install Flask Flask-SQLAlchemy PyMySQL Sastrawi PyPDF2 python-docx
```

### 3️⃣ Setup Frontend (Tailwind CSS)

**Install dependensi Node.js:**

```bash
npm install
```

### 4️⃣ Setup Database

**Buat database MySQL:**

```sql
CREATE DATABASE db_search_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Konfigurasi koneksi database:**

Edit file `app.py` dan sesuaikan connection string MySQL:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/tokenverse_db'
```

**Inisialisasi database dan isi data awal:**

```bash
python3 populate_db.py
```

### 5️⃣ Menjalankan Aplikasi

**Anda perlu membuka DUA terminal:**

**Terminal 1 - Jalankan Tailwind CSS (untuk kompilasi CSS):**

```bash
npm run dev
```

**Terminal 2 - Jalankan Flask Server:**

```bash
python3 app.py
```

**Akses aplikasi di browser:**

```
http://localhost:5000
```

---

## 📖 Cara Penggunaan

1. **Pencarian Dokumen**: Masukkan kata kunci di kolom pencarian pada halaman utama
2. **Upload Dokumen Baru**: Gunakan fitur upload untuk menambahkan dokumen baru ke dalam sistem
3. **Lihat Hasil**: Sistem akan menampilkan dokumen yang relevan berdasarkan skor TF-IDF tertinggi

---

## 🔧 Konfigurasi

Anda dapat mengubah beberapa konfigurasi di file `app.py`:

```python
# Folder untuk menyimpan file upload
UPLOAD_FOLDER = 'uploads'

# Maksimal ukuran file upload (16 MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Format file yang diizinkan
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
```

---

## 🧪 Algoritma TF-IDF

Sistem ini menggunakan algoritma TF-IDF untuk menghitung relevansi dokumen:

- **TF (Term Frequency)**: Frekuensi kemunculan term dalam dokumen
- **IDF (Inverse Document Frequency)**: Tingkat kepentingan term di seluruh koleksi
- **Formula**: `TF-IDF = TF × log(N / DF)`

Di mana:
- `N` = Total jumlah dokumen
- `DF` = Jumlah dokumen yang mengandung term

---

## 🤝 Kontribusi

Kontribusi selalu diterima dengan tangan terbuka! Jika Anda ingin berkontribusi:

1. Fork repositori ini
2. Buat branch fitur baru (`git checkout -b fitur-baru`)
3. Commit perubahan Anda (`git commit -m 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

---

## 📝 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE). Anda bebas menggunakan, memodifikasi, dan mendistribusikan kode ini dengan tetap mencantumkan kredit kepada pembuat asli.

---

## 👨‍💻 Penulis

**Nama Anda**
- GitHub: [@PutraKrishna](https://github.com/PutraKrishna)
- Email: putrakrishna932@gamil.com

---

## 🙏 Acknowledgments

- Terima kasih kepada tim [Sastrawi](https://github.com/sastrawi/sastrawi) untuk library stemming bahasa Indonesia
- Inspirasi dari sistem information retrieval modern
- Komunitas open source yang luar biasa

---

<div align="center">
  
**⭐ Jika proyek ini membantu Anda, jangan lupa untuk memberikan star!**

Made with ❤️ and ☕ in Indonesia

</div>



