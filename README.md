# Klasifikasi Kondisi Cuaca Menggunakan CNN (Convolutional Neural Network)

Repositori GitHub: [https://github.com/naufalfarel/Klasifikasi-Kondisi-Cuaca-Menggunakan-CNN](https://github.com/naufalfarel/Klasifikasi-Kondisi-Cuaca-Menggunakan-CNN)

Proyek ini dibuat untuk memenuhi Ujian Akhir Semester (UAS) mata kuliah Machine Learning / Deep Learning, Program Studi Informatika, Universitas Syiah Kuala (USK).

---

## 👥 Anggota Tim (Kelompok 8)
- **Muhammad Nazlul Ramadhyan** (2308107010036)
- **Naufal Farrel Syafilan** (2308107010058)

---

## 📝 Deskripsi Proyek
Aplikasi ini melakukan klasifikasi kondisi cuaca berdasarkan input gambar secara real-time. Cuaca diklasifikasikan ke dalam **3 kelas**:
1. ☁️ **Berawan (Cloudy)**
2. 🌧️ **Hujan (Rain)**
3. ☀️ **Cerah (Shine)**

### Eksperimen & Performa Model:
Selama pengerjaan, kami mengevaluasi 3 arsitektur model CNN:
*   **Model 1 (CNN Dasar/Baseline)**: Akurasi **85.5%** | F1-Score **84.9%**
*   **Model 2 (CNN + Dropout)**: Akurasi **91.1%** | F1-Score **91.1%** (Model terbaik yang digunakan)
*   **Model 3 (CNN + Augmentasi)**: Akurasi **53.3%** | F1-Score **47.3%** (Menurun drastis akibat gangguan augmentasi visual berlebih)

---

## ⚙️ Arsitektur Penerapan (Deployment)
Sistem dideploy secara terpisah untuk backend dan frontend demi efisiensi resource:
1.  **Backend API (FastAPI)**: Memuat model CNN (.h5), menerima file gambar, melakukan preprocessing ke ukuran 150x150 piksel, dan mengirimkan hasil klasifikasi beserta confidence score.
2.  **Frontend Web App (Streamlit)**: Antarmuka berbasis web yang ramah pengguna untuk mengunggah file gambar (JPG/PNG) dan menampilkan visualisasi bar persentase hasil prediksi.

---

## 🚀 Instruksi Penerapan (Cara Menjalankan)

### 1. Prasyarat (Prerequisites)
Pastikan Anda sudah menginstal **Python 3.8** atau versi terbaru di sistem Anda.

### 2. Kloning Repositori
```bash
git clone https://github.com/naufalfarel/Klasifikasi-Kondisi-Cuaca-Menggunakan-CNN.git
cd Klasifikasi-Kondisi-Cuaca-Menggunakan-CNN
```

### 3. Instalasi Dependensi
Instal semua package yang diperlukan untuk API dan aplikasi web:
```bash
pip install -r requirements.txt
```

### 4. Menjalankan Backend (FastAPI)
Jalankan server FastAPI secara lokal:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
API akan berjalan di `http://localhost:8000`. Anda dapat mengakses dokumentasi interaktif Swagger API di `http://localhost:8000/docs`.

### 5. Menjalankan Frontend (Streamlit)
Buka terminal baru dan jalankan antarmuka Streamlit:
```bash
streamlit run app.py
```
Aplikasi web akan terbuka secara otomatis di browser Anda pada alamat `http://localhost:8501`.

---

## ☁️ Penerapan di Cloud (Deployment to Render)
Proyek ini telah dideploy secara online di platform **Render**. 

> [!IMPORTANT]
> Karena menggunakan layanan Render Free Tier, server backend akan memasuki mode *sleep* jika tidak mendeteksi aktivitas. 
> Untuk membukanya pertama kali, **ikuti alur berikut**:
>
> 1. Buka URL Backend (FastAPI) terlebih dahulu: **[https://fastapi-weather-vtja.onrender.com/](https://fastapi-weather-vtja-onrender-com.onrender.com)** (Tunggu beberapa saat sampai web memuat pesan aktif `{"message": "..."}`).
> 2. Buka URL Frontend (Streamlit): **[https://streamlit-weather.onrender.com/](https://streamlit-weather.onrender.com/)** untuk mencoba klasifikasi cuaca.

### Konfigurasi Deployment:
Proyek ini menggunakan file `render.yaml` untuk deployment otomatis:
- **FastAPI Service**: Dideploy sebagai Web Service (Backend).
- **Streamlit Service**: Dideploy sebagai Web Service (Frontend) yang terhubung ke environment URL FastAPI yang telah dideploy.
