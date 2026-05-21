from flask import Flask, render_template, request, redirect, url_for, flash
from collections import deque, Counter
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "kantinith"

# ======================= DATABASE SEMENTARA =======================
menu_database = {}
antrian_pesanan = deque()
riwayat_selesai = []

histori_makanan_terpesan = []
histori_mahasiswa_memesan = []
histori_nominal_transaksi = []
user_profil = {
    "nama": "Andi Ahmad",
    "nim": "250209001",
    "kelas": "Prodi-ILKOM-A",
    "hp": "081234567890"
}

keranjang_belanja = []

# ======================= GENERATE DATA =======================
def generate_data_awal():
    kategori_opsi = ["Makanan", "Minuman", "Snack", "Dessert"]

    sampel_makanan = {
        "Makanan": ["Nasi Goreng Kampus", "Ayam Geprek ITH", "Mie Titi", "Bakso Granat", "Soto Ayam"],
        "Minuman": ["Es Teh Manis", "Jus Alpukat", "Kopi Gula Aren", "Matcha Latte"],
        "Snack": ["Roti Bakar", "Pisang Peppe Keju", "Kentang Goreng"],
        "Dessert": ["Puding Cokelat", "Salad Buah", "Ice Cream Waffle"]
    }

    for i in range(1, 51):
        kat = random.choice(kategori_opsi)
        nama_item = f"{random.choice(sampel_makanan[kat])} Spesial V-{i}"
        kode = f"MN{i:03d}"
        harga = random.choice([6000, 8000, 10000, 12000, 15000, 20000])

        menu_database[kode] = {
            "kode": kode,
            "nama": nama_item,
            "harga": harga,
            "kategori": kat,
            "stok": random.randint(10, 40)
        }

# ======================= HOME =======================
@app.route('/')
def index():
    return render_template('index.html')

# ======================= MAHASISWA =======================
@app.route('/mahasiswa')
def mahasiswa():
    keyword = request.args.get('search', '').lower()

    data_menu = list(menu_database.values())

    if keyword:
        data_menu = [
            item for item in data_menu
            if keyword in item['nama'].lower()
            or keyword in item['kategori'].lower()
        ]

    total = sum(item['harga'] for item in keranjang_belanja)

    return render_template(
        'mahasiswa.html',
        menu=data_menu,
        keranjang=keranjang_belanja,
        total=total,
        profil=user_profil,
        antrian=antrian_pesanan,
        selesai=riwayat_selesai
    )

# ======================= TAMBAH KERANJANG =======================
@app.route('/tambah/<kode>')
def tambah_keranjang(kode):
    item = menu_database.get(kode)

    if item:
        if item['stok'] > 0:
            keranjang_belanja.append(item)
            flash('Menu berhasil ditambahkan!', 'success')
        else:
            flash('Stok habis!', 'danger')

    return redirect(url_for('mahasiswa'))

# ======================= KOSONGKAN KERANJANG =======================
@app.route('/kosongkan')
def kosongkan():
    keranjang_belanja.clear()
    flash('Keranjang dikosongkan!', 'warning')
    return redirect(url_for('mahasiswa'))

# ======================= CHECKOUT =======================
@app.route('/checkout', methods=['POST'])
def checkout():
    if not keranjang_belanja:
        flash('Keranjang kosong!', 'danger')
        return redirect(url_for('mahasiswa'))

    metode = request.form.get('metode')

    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    total = sum(item['harga'] for item in keranjang_belanja)

    daftar_kode = []

    for item in keranjang_belanja:
        daftar_kode.append(item['kode'])
        menu_database[item['kode']]['stok'] -= 1

    pesanan = {
        'id': random.randint(1000, 9999),
        'nama': user_profil['nama'],
        'nim': user_profil['nim'],
        'items': daftar_kode,
        'total': total,
        'waktu': waktu,
        'metode': metode,
        'status': 'Menunggu Konfirmasi'
    }
    antrian_pesanan.append(pesanan)

    histori_mahasiswa_memesan.append(user_profil['nama'])
    histori_nominal_transaksi.append(total)
    histori_makanan_terpesan.extend(daftar_kode)

    keranjang_belanja.clear()

    flash('Checkout berhasil!', 'success')

    return redirect(url_for('mahasiswa'))

# ======================= ADMIN =======================
@app.route('/admin')
def admin():
    total_omset = sum(histori_nominal_transaksi)

    top_menu = Counter(histori_makanan_terpesan).most_common(3)
    top_pelanggan = Counter(histori_mahasiswa_memesan).most_common(3)

    return render_template(
        'admin.html',
        antrian=antrian_pesanan, 
         menu=menu_database.values(),
        omset=total_omset,
        top_menu=top_menu,
        top_pelanggan=top_pelanggan
    )

# ======================= SELESAIKAN PESANAN =======================
@app.route('/selesai/<int:id>')
def selesai(id):
    for pesanan in list(antrian_pesanan):
        if pesanan['id'] == id:
            pesanan['status'] = 'Selesai'
            riwayat_selesai.append(pesanan)
            antrian_pesanan.remove(pesanan)
            break

    flash('Pesanan selesai!', 'success')
    return redirect(url_for('admin'))

# ======================= TAMBAH MENU =======================
@app.route('/tambah_menu', methods=['POST'])
def tambah_menu():
    nama = request.form['nama']
    kategori = request.form['kategori']
    harga = int(request.form['harga'])
    stok = int(request.form['stok'])

    kode = f"MN{len(menu_database)+1:03d}"

    menu_database[kode] = {
        'kode': kode,
        'nama': nama,
        'kategori': kategori,
        'harga': harga,
        'stok': stok
    }

    flash('Menu berhasil ditambahkan!', 'success')
    return redirect(url_for('admin'))

# ======================= MAIN =======================
if __name__ == '__main__':
    generate_data_awal()
    app.run(debug=True)