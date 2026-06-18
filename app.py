import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ganti_dengan_kunci_rahasia_yang_kuat')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login terlebih dahulu.'

class User(UserMixin):
    def __init__(self, id, username, nama_lengkap, role):
        self.id = id
        self.username = username
        self.nama_lengkap = nama_lengkap
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = database.get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['nama_lengkap'], user['role'])
    return None

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Halaman ini khusus admin.', 'danger')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = database.get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username'], user['nama_lengkap'], user['role']))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Username atau password salah.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = database.get_db()
    if current_user.role == 'admin':
        santri_list = conn.execute('SELECT * FROM santri ORDER BY id DESC').fetchall()
    else:
        santri_list = conn.execute('SELECT * FROM santri WHERE created_by = ? ORDER BY id DESC', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', santri_list=santri_list)

@app.route('/tambah', methods=['GET', 'POST'])
@login_required
def tambah():
    if request.method == 'POST':
        data = (
            request.form['nama'],
            request.form['nis'],
            request.form['kelas'],
            request.form['asrama'],
            request.form['bulan'],
            request.form['tahun'],
            int(request.form.get('md_hadir', 0)),
            int(request.form.get('md_izin', 0)),
            int(request.form.get('md_sakit', 0)),
            int(request.form.get('md_alpa', 0)),
            int(request.form.get('md_total', 0)),
            int(request.form.get('hf_hadir', 0)),
            int(request.form.get('hf_izin', 0)),
            int(request.form.get('hf_sakit', 0)),
            int(request.form.get('hf_alpa', 0)),
            int(request.form.get('hf_total', 0)),
            int(request.form.get('fm_hadir', 0)),
            int(request.form.get('fm_izin', 0)),
            int(request.form.get('fm_sakit', 0)),
            int(request.form.get('fm_alpa', 0)),
            int(request.form.get('fm_total', 0)),
            request.form['adab_guru'],
            request.form['adab_sesama'],
            request.form['kedisiplinan'],
            request.form['kerapian'],
            request.form['tanggung_jawab'],
            request.form['kejujuran'],
            request.form['kemandirian'],
            request.form['kepatuhan'],
            request.form['catatan_pembina'],
            1 if 'pembinaan_khusus' in request.form else 0,
            1 if 'pendampingan_intensif' in request.form else 0,
            1 if 'monitoring_lanjutan' in request.form else 0,
            1 if 'apresiasi' in request.form else 0,
            request.form['keterangan_tambahan'],
            request.form['tanggal'],
            current_user.id
        )
        conn = database.get_db()
        conn.execute('''
            INSERT INTO santri (
                nama, nis, kelas, asrama, bulan, tahun,
                md_hadir, md_izin, md_sakit, md_alpa, md_total,
                hf_hadir, hf_izin, hf_sakit, hf_alpa, hf_total,
                fm_hadir, fm_izin, fm_sakit, fm_alpa, fm_total,
                adab_guru, adab_sesama, kedisiplinan, kerapian,
                tanggung_jawab, kejujuran, kemandirian, kepatuhan,
                catatan_pembina,
                pembinaan_khusus, pendampingan_intensif, monitoring_lanjutan, apresiasi,
                keterangan_tambahan, tanggal, created_by
            ) VALUES (?,?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?, ?,?,?,?,?, ?,?,?)
        ''', data)
        conn.commit()
        conn.close()
        flash('Data santri berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
    return render_template('form.html', title='Tambah Santri', santri=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    conn = database.get_db()
    santri = conn.execute('SELECT * FROM santri WHERE id=?', (id,)).fetchone()
    if not santri:
        flash('Data tidak ditemukan.', 'danger')
        return redirect(url_for('index'))
    if current_user.role != 'admin' and santri['created_by'] != current_user.id:
        flash('Anda tidak berhak mengedit data ini.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        data = (
            request.form['nama'],
            request.form['nis'],
            request.form['kelas'],
            request.form['asrama'],
            request.form['bulan'],
            request.form['tahun'],
            int(request.form.get('md_hadir', 0)),
            int(request.form.get('md_izin', 0)),
            int(request.form.get('md_sakit', 0)),
            int(request.form.get('md_alpa', 0)),
            int(request.form.get('md_total', 0)),
            int(request.form.get('hf_hadir', 0)),
            int(request.form.get('hf_izin', 0)),
            int(request.form.get('hf_sakit', 0)),
            int(request.form.get('hf_alpa', 0)),
            int(request.form.get('hf_total', 0)),
            int(request.form.get('fm_hadir', 0)),
            int(request.form.get('fm_izin', 0)),
            int(request.form.get('fm_sakit', 0)),
            int(request.form.get('fm_alpa', 0)),
            int(request.form.get('fm_total', 0)),
            request.form['adab_guru'],
            request.form['adab_sesama'],
            request.form['kedisiplinan'],
            request.form['kerapian'],
            request.form['tanggung_jawab'],
            request.form['kejujuran'],
            request.form['kemandirian'],
            request.form['kepatuhan'],
            request.form['catatan_pembina'],
            1 if 'pembinaan_khusus' in request.form else 0,
            1 if 'pendampingan_intensif' in request.form else 0,
            1 if 'monitoring_lanjutan' in request.form else 0,
            1 if 'apresiasi' in request.form else 0,
            request.form['keterangan_tambahan'],
            request.form['tanggal'],
            id
        )
        conn.execute('''
            UPDATE santri SET
                nama=?, nis=?, kelas=?, asrama=?, bulan=?, tahun=?,
                md_hadir=?, md_izin=?, md_sakit=?, md_alpa=?, md_total=?,
                hf_hadir=?, hf_izin=?, hf_sakit=?, hf_alpa=?, hf_total=?,
                fm_hadir=?, fm_izin=?, fm_sakit=?, fm_alpa=?, fm_total=?,
                adab_guru=?, adab_sesama=?, kedisiplinan=?, kerapian=?,
                tanggung_jawab=?, kejujuran=?, kemandirian=?, kepatuhan=?,
                catatan_pembina=?,
                pembinaan_khusus=?, pendampingan_intensif=?, monitoring_lanjutan=?, apresiasi=?,
                keterangan_tambahan=?, tanggal=?
            WHERE id=?
        ''', data)
        conn.commit()
        conn.close()
        flash('Data berhasil diperbarui!', 'success')
        return redirect(url_for('index'))
    conn.close()
    return render_template('form.html', title='Edit Santri', santri=santri)

@app.route('/hapus/<int:id>')
@login_required
def hapus(id):
    conn = database.get_db()
    santri = conn.execute('SELECT * FROM santri WHERE id=?', (id,)).fetchone()
    if not santri:
        flash('Data tidak ditemukan.', 'danger')
        return redirect(url_for('index'))
    if current_user.role != 'admin' and santri['created_by'] != current_user.id:
        flash('Anda tidak berhak menghapus data ini.', 'danger')
        return redirect(url_for('index'))
    conn.execute('DELETE FROM santri WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Data dihapus.', 'danger')
    return redirect(url_for('index'))

@app.route('/raport/<int:id>')
@login_required
def raport(id):
    conn = database.get_db()
    santri = conn.execute('SELECT * FROM santri WHERE id=?', (id,)).fetchone()
    conn.close()
    if not santri:
        flash('Santri tidak ditemukan!', 'danger')
        return redirect(url_for('index'))
    if current_user.role != 'admin' and santri['created_by'] != current_user.id:
        flash('Anda tidak berhak melihat raport ini.', 'danger')
        return redirect(url_for('index'))
    return render_template('raport.html', s=santri)

# ---------- MANAJEMEN USER (khusus admin) ----------
@app.route('/users')
@login_required
@admin_required
def user_list():
    conn = database.get_db()
    users = conn.execute('SELECT * FROM users ORDER BY id').fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/users/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def user_tambah():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nama_lengkap = request.form['nama_lengkap']
        role = request.form['role']
        conn = database.get_db()
        existing = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if existing:
            flash('Username sudah dipakai.', 'danger')
            conn.close()
            return render_template('user_form.html', title='Tambah User', user=None)
        hashed = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, password_hash, nama_lengkap, role) VALUES (?, ?, ?, ?)',
            (username, hashed, nama_lengkap, role)
        )
        conn.commit()
        conn.close()
        flash('Akun guru berhasil dibuat!', 'success')
        return redirect(url_for('user_list'))
    return render_template('user_form.html', title='Tambah Akun Guru', user=None)

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    conn = database.get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (id,)).fetchone()
    if not user:
        flash('User tidak ditemukan.', 'danger')
        return redirect(url_for('user_list'))
    if request.method == 'POST':
        username = request.form['username']
        nama_lengkap = request.form['nama_lengkap']
        role = request.form['role']
        password = request.form.get('password')
        existing = conn.execute('SELECT * FROM users WHERE username=? AND id!=?', (username, id)).fetchone()
        if existing:
            flash('Username sudah dipakai user lain.', 'danger')
            conn.close()
            return render_template('user_form.html', title='Edit User', user=user)
        if password and password.strip() != '':
            hashed = generate_password_hash(password)
            conn.execute(
                'UPDATE users SET username=?, password_hash=?, nama_lengkap=?, role=? WHERE id=?',
                (username, hashed, nama_lengkap, role, id)
            )
        else:
            conn.execute(
                'UPDATE users SET username=?, nama_lengkap=?, role=? WHERE id=?',
                (username, nama_lengkap, role, id)
            )
        conn.commit()
        conn.close()
        flash('Akun berhasil diperbarui.', 'success')
        return redirect(url_for('user_list'))
    conn.close()
    return render_template('user_form.html', title='Edit User', user=user)

@app.route('/users/hapus/<int:id>')
@login_required
@admin_required
def user_hapus(id):
    if id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri.', 'danger')
        return redirect(url_for('user_list'))
    conn = database.get_db()
    conn.execute('DELETE FROM users WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Akun dihapus.', 'danger')
    return redirect(url_for('user_list'))

if __name__ == '__main__':
    database.init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))