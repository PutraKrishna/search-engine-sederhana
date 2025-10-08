TokenVerse 
TokenVerse adalah sebuah sistem information retrieval (mesin pencari) yang dibangun menggunakan Python dan Flask. Sistem ini mampu mengindeks koleksi dokumen digital (seperti .txt, .pdf, .docx) dan melakukan pencarian berdasarkan relevansi menggunakan algoritma ranking TF-IDF.

Fitur Utama
Ranking Berbasis TF-IDF: Hasil pencarian diurutkan berdasarkan skor relevansi yang dihitung dari Term Frequency (TF) dan Inverse Document Frequency (IDF), memberikan hasil yang lebih akurat daripada pencarian berbasis frekuensi sederhana.

Dukungan Multi-Format: Mampu membaca, mengekstrak teks, dan mengindeks dokumen dalam format .txt, .pdf, dan .docx.

Preprocessing Teks Bahasa Indonesia: Melakukan tokenisasi, stopword removal, dan stemming khusus untuk Bahasa Indonesia menggunakan pustaka Sastrawi.

Antarmuka Pengguna Interaktif: UI yang bersih dan responsif dibangun dengan HTML dan Tailwind CSS.

Manajemen Data Dinamis: Pengguna dapat mengunggah dokumen baru melalui antarmuka web, yang akan secara otomatis diindeks dan bisa langsung dicari.

Penyimpanan Persisten: Menggunakan MySQL untuk menyimpan semua data dokumen dan indeks pencarian.

Arsitektur & Teknologi
Komponen

Teknologi

Backend

Python, Flask

Frontend

HTML, Tailwind CSS

Database

MySQL

ORM

Flask-SQLAlchemy

NLP

Sastrawi

Ekstraksi

PyPDF2, python-docx

Struktur Proyek
/
├── app.py             # Pusat kendali aplikasi web (Routes & Logika Utama)
├── models.py          # Definisi "cetak biru" untuk tabel database (SQLAlchemy Models)
├── utils.py           # Berisi fungsi-fungsi pembantu (ekstraksi teks, preprocessing)
├── populate_db.py     # Skrip untuk mengisi database dengan data awal
├── templates/         # Berisi file-file HTML
├── static/            # Berisi file CSS, JavaScript, dan gambar
├── koleksi_data/      # Folder default untuk menyimpan dokumen
├── requirements.txt   # Daftar library Python yang dibutuhkan
└── package.json       # Daftar library Node.js yang dibutuhkan (untuk Tailwind)


Cara Instalasi dan Menjalankan Proyek
Prasyarat
Sebelum memulai, pastikan perangkat Anda sudah terinstal:

Git

Python 3.x

Node.js dan npm

Server MySQL

1. Clone Repositori
git clone [https://github.com/](https://github.com/)[username-anda]/[nama-repositori-anda].git
cd [nama-repositori-anda]


2. Setup Backend (Python)
Buat dan aktifkan virtual environment, lalu instal semua library yang dibutuhkan.

# Buat virtual environment
python3 -m venv venv

# Aktifkan (untuk macOS/Linux)
source venv/bin/activate
# Aktifkan (untuk Windows)
# venv\Scripts\activate

# Instal semua library dari requirements.txt
pip install -r requirements.txt


3. Setup Frontend (Tailwind CSS)
Instal semua dependensi Node.js yang diperlukan.

npm install


4. Setup Database (MySQL)
Buka tool database Anda (phpMyAdmin, DBeaver, dll).

Buat database baru dengan nama db_search_engine dan collation utf8mb4_unicode_ci.

Pastikan detail koneksi (user, password, host) sesuai dengan yang ada di app.py atau atur melalui environment variables.

Jalankan skrip populate_db.py untuk mengisi database dengan data awal dari folder koleksi_data.

# Pastikan venv sudah aktif
python3 populate_db.py


5. Menjalankan Aplikasi
Anda perlu menjalankan dua proses di dua terminal terpisah.

Di Terminal 1 (untuk Frontend):

# Jalankan proses build Tailwind CSS
npm run dev


Di Terminal 2 (untuk Backend):

# Jalankan server Flask
python3 app.py

