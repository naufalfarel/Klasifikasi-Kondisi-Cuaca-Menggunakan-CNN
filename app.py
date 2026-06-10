import os
import io
import requests
import streamlit as st
from PIL import Image

# ─────────────────────────────────────────────
# Konfigurasi URL FastAPI
# Saat deploy di Render, ubah FASTAPI_URL lewat
# Environment Variable di dashboard Render.
# ─────────────────────────────────────────────
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# ─────────────────────────────────────────────
# Mapping label → emoji & deskripsi
# ─────────────────────────────────────────────
LABEL_INFO = {
    "cloudy": {
        "emoji": "☁️",
        "label_id": "Berawan",
        "desc": "Langit tertutup awan tebal tanpa matahari yang terlihat jelas.",
        "color": "#6c757d",
    },
    "rain": {
        "emoji": "🌧️",
        "label_id": "Hujan",
        "desc": "Kondisi cuaca dengan curah hujan atau awan hujan yang dominan.",
        "color": "#0d6efd",
    },
    "shine": {
        "emoji": "☀️",
        "label_id": "Cerah",
        "desc": "Langit cerah dengan sinar matahari yang bersinar terang.",
        "color": "#fd7e14",
    },
}

# ─────────────────────────────────────────────
# Halaman Streamlit
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Klasifikasi Cuaca CNN",
    page_icon="🌤️",
    layout="centered",
)

# ── Header ──────────────────────────────────
st.title("🌤️ Klasifikasi Kondisi Cuaca")
st.markdown(
    "Upload foto cuaca, dan model CNN akan memprediksi kondisinya: "
    "**Berawan**, **Hujan**, atau **Cerah**."
)
st.markdown("---")

# ── Sidebar info ────────────────────────────
with st.sidebar:
    st.header("ℹ️ Tentang Aplikasi")
    st.markdown(
        """
        Klasifikasi kondisi cuaca dari gambar menggunakan CNN.

        **Kelas yang didukung:**
        - ☁️ Berawan
        - 🌧️ Hujan
        - ☀️ Cerah

        ---
        *Kelompok 8 – Informatika USK*
        """
    )

    st.markdown("---")
    st.caption("Tips: Gunakan foto outdoor yang jelas untuk hasil terbaik.")

# ── Upload area ──────────────────────────────
uploaded_file = st.file_uploader(
    "Pilih gambar (JPG / PNG / WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload satu gambar kondisi cuaca untuk diprediksi.",
)

if uploaded_file is not None:
    # Tampilkan preview gambar
    image = Image.open(uploaded_file).convert("RGB")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption=f"📷 {uploaded_file.name}", use_container_width=True)

    st.markdown("---")

    # ── Tombol prediksi ──────────────────────
    if st.button("🔍 Prediksi Cuaca", use_container_width=True, type="primary"):
        with st.spinner("Menganalisis gambar..."):
            # Kirim ke FastAPI
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            try:
                response = requests.post(
                    f"{FASTAPI_URL}/predict",
                    files={"file": (uploaded_file.name, img_bytes, "image/jpeg")},
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    label = result["predicted_label"]
                    confidence = result["confidence"]
                    all_probs = result["all_probabilities"]

                    info = LABEL_INFO.get(label, {
                        "emoji": "❓",
                        "label_id": label.title(),
                        "desc": "",
                        "color": "#333",
                    })

                    # ── Kotak hasil prediksi ──────────────
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {info['color']}18;
                            border-left: 5px solid {info['color']};
                            border-radius: 8px;
                            padding: 20px 24px;
                            margin-bottom: 16px;
                        ">
                            <h2 style="margin: 0; color: {info['color']};">
                                {info['emoji']} {info['label_id']}
                            </h2>
                            <p style="margin: 6px 0 0 0; font-size: 15px; color: #555;">
                                {info['desc']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # ── Confidence score ──────────────────
                    st.subheader("📊 Confidence Score")
                    st.metric(
                        label=f"Prediksi: {info['label_id']}",
                        value=f"{confidence:.2f}%",
                    )
                    st.progress(confidence / 100)

                    # ── Bar chart semua kelas ─────────────
                    st.subheader("📈 Probabilitas Semua Kelas")
                    for cls, prob in sorted(all_probs.items(), key=lambda x: -x[1]):
                        cls_info = LABEL_INFO.get(cls, {})
                        emoji = cls_info.get("emoji", "")
                        label_id = cls_info.get("label_id", cls.title())
                        color = cls_info.get("color", "#888")
                        bar_width = max(prob, 1)

                        st.markdown(
                            f"""
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                    <span style="font-weight: 600;">{emoji} {label_id}</span>
                                    <span style="color: {color}; font-weight: 700;">{prob:.2f}%</span>
                                </div>
                                <div style="background: #e9ecef; border-radius: 4px; height: 10px;">
                                    <div style="
                                        width: {bar_width}%;
                                        background: {color};
                                        height: 10px;
                                        border-radius: 4px;
                                        transition: width 0.5s;
                                    "></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                elif response.status_code == 400:
                    st.error(f"⚠️ {response.json().get('detail', 'Format gambar tidak didukung.')}")
                else:
                    st.error(f"❌ Terjadi kesalahan pada server (HTTP {response.status_code}).")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Tidak dapat terhubung ke API. "
                    f"Pastikan FastAPI berjalan di `{FASTAPI_URL}`."
                )
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timeout. Server terlalu lama merespons.")
            except Exception as e:
                st.error(f"❌ Error tidak terduga: {str(e)}")

else:
    # Tampilkan placeholder saat belum ada gambar
    st.markdown(
        """
        <div style="
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            color: #aaa;
            font-size: 16px;
        ">
            📂 Upload gambar cuaca di atas untuk memulai prediksi
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ───────────────────────────────────
st.markdown("---")
st.caption("Kelompok 8 – Informatika USK | Tugas UAS Machine Learning / Deep Learning")
