import os
import io
import numpy as np
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import tensorflow as tf

# ─────────────────────────────────────────────
# Konfigurasi (sesuai notebook Tugas 3)
# ─────────────────────────────────────────────
IMG_SIZE = (150, 150)
CLASS_NAMES = ["cloudy", "rain", "shine"]   # urutan alphabetical = urutan TF
MODEL_PATH = Path("model_cnn_cuaca_terbaik.h5")

# ─────────────────────────────────────────────
# Inisialisasi FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title="Weather CNN API",
    description="API prediksi kondisi cuaca menggunakan CNN (Tugas 3 - Kelompok 8)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Load model saat startup
# ─────────────────────────────────────────────
model = None

@app.on_event("startup")
def load_model():
    global model
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"File model tidak ditemukan: {MODEL_PATH}. "
            "Pastikan model_cnn_cuaca_terbaik.h5 ada di root folder."
        )
    model = tf.keras.models.load_model(str(MODEL_PATH))
    print(f"✅ Model berhasil dimuat dari: {MODEL_PATH}")


# ─────────────────────────────────────────────
# Helper: preprocessing gambar
# ─────────────────────────────────────────────
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Buka gambar dari bytes, resize ke 150x150 RGB,
    ubah ke array float32, tambahkan dimensi batch.
    Normalisasi (rescaling 1/255) dilakukan di dalam model
    via layer Rescaling sehingga di sini TIDAK perlu dibagi 255.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)                  # (150, 150)
    arr = np.array(img, dtype=np.float32)       # (150, 150, 3)
    arr = np.expand_dims(arr, axis=0)            # (1, 150, 150, 3)
    return arr


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Weather CNN API aktif. Gunakan POST /predict untuk prediksi."}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Validasi tipe file
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipe file tidak didukung: {file.content_type}. Gunakan JPG, PNG, atau WEBP.",
        )

    if model is None:
        raise HTTPException(status_code=503, detail="Model belum siap, coba lagi.")

    # Baca dan proses gambar
    image_bytes = await file.read()
    try:
        input_array = preprocess_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gambar tidak dapat diproses: {str(e)}")

    # Prediksi
    predictions = model.predict(input_array, verbose=0)   # shape: (1, 3)
    probabilities = predictions[0]                         # shape: (3,)

    predicted_index = int(np.argmax(probabilities))
    predicted_label = CLASS_NAMES[predicted_index]
    confidence = float(probabilities[predicted_index]) * 100

    # Semua probabilitas per kelas
    all_probs = {
        CLASS_NAMES[i]: round(float(probabilities[i]) * 100, 2)
        for i in range(len(CLASS_NAMES))
    }

    return JSONResponse({
        "predicted_label": predicted_label,
        "confidence": round(confidence, 2),
        "all_probabilities": all_probs,
        "filename": file.filename,
    })
