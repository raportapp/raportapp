import sqlite3
import os
from werkzeug.security import generate_password_hash

# Gunakan volume Railway jika ada, fallback ke folder lokal
DATA_DIR = os.environ.get('RAILWAY_VOLUME_MOUNT_PATH', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'santri.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Pastikan folder data ada
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabel santri
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS santri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nis TEXT,
            kelas TEXT,
            asrama TEXT,
            bulan TEXT,
            tahun TEXT,
            md_hadir INTEGER DEFAULT 0,
            md_izin INTEGER DEFAULT 0,
            md_sakit INTEGER DEFAULT 0,
            md_alpa INTEGER DEFAULT 0,
            md_total INTEGER DEFAULT 0,
            hf_hadir INTEGER DEFAULT 0,
            hf_izin INTEGER DEFAULT 0,
            hf_sakit INTEGER DEFAULT 0,
            hf_alpa INTEGER DEFAULT 0,
            hf_total INTEGER DEFAULT 0,
            fm_hadir INTEGER DEFAULT 0,
            fm_izin INTEGER DEFAULT 0,
            fm_sakit INTEGER DEFAULT 0,
            fm_alpa INTEGER DEFAULT 0,
            fm_total INTEGER DEFAULT 0,
            adab_guru TEXT,
            adab_sesama TEXT,
            kedisiplinan TEXT,
            kerapian TEXT,
            tanggung_jawab TEXT,
            kejujuran TEXT,
            kemandirian TEXT,
            kepatuhan TEXT,
            catatan_pembina TEXT,
            pembinaan_khusus INTEGER DEFAULT 0,
            pendampingan_intensif INTEGER DEFAULT 0,
            monitoring_lanjutan INTEGER DEFAULT 0,
            apresiasi INTEGER DEFAULT 0,
            keterangan_tambahan TEXT,
            tanggal TEXT,
            created_by INTEGER
        )
    ''')
    
    # Tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama_lengkap TEXT,
            role TEXT DEFAULT 'guru'
        )
    ''')
    
    # Buat admin default jika belum ada
    admin = cursor.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not admin:
        hashed = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (username, password_hash, nama_lengkap, role) VALUES (?, ?, ?, ?)",
            ('admin', hashed, 'Administrator Utama', 'admin')
        )
        print("Admin default dibuat: username=admin, password=admin123")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()