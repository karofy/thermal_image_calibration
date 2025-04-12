import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile

st.set_page_config(page_title="Thermal Calibration", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
        .logo-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding: 10px 30px;
        }
        .logo-container img {
            height: 120px;
        }
    </style>

    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/karofy/thermal_image_calibration/refs/heads/master/assets/856x973_ESCUDOCOLOR.png" alt="Left Logo">
        <img src="https://raw.githubusercontent.com/karofy/thermal_image_calibration/refs/heads/master/assets/logo_TyC.png" alt="Right Logo">
    </div>
""", unsafe_allow_html=True)


st.markdown(""" 
    <style>
        @import url('https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&display=swap');

        body {
            background: linear-gradient(to bottom right, #1e3c72, #2a5298);
            color: white;
            font-family: 'PT Serif', serif;
        }

        h1 {
            text-align: center;
            color: #ffcc00;
            font-size: 40px;
        }

        .stButton > button {
            background-color: #ffa500;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            font-family: 'PT Serif', serif;
        }

        .stDownloadButton > button {
            background-color: #28a745;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            font-family: 'PT Serif', serif;
        }

        .stNumberInput input {
            background-color: #f0f0f0;
            color: #333;
            font-family: 'PT Serif', serif;
        }

        h2, h3, .stMarkdown {
            color: #f0f0f0;
            font-family: 'PT Serif', serif;
        }

        .stFileUploader {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("<h1 style='text-align: center; color: #ff6600;'>🌡️ Thermal Image Calibration</h1>", unsafe_allow_html=True)
st.write("This app allows you to upload a thermal orthomosaic, apply a **calibration equation**, and visualize the results.")

# --- NUEVO: Menús desplegables ---
st.subheader("🗺️ Select flight info")
zona = st.selectbox("📍 Study Zone", ["Ferreñafe", "Chongoyape"])
vuelo = st.selectbox("🕹️ Flight Number", [1, 2, 3, 4, 5])
hora = st.time_input("🕒 Flight Time (24h format )")

# --- Diccionario de ecuaciones ---
# Formato: (zona, vuelo) : (A, B)
ecuaciones = {
    ("Ferreñafe", 1): (0.6341, 11.887),
    ("Ferreñafe", 2): (0.8746, 12.76),
    ("Ferreñafe", 3): (0.7291, 10.592),
    ("Ferreñafe", 4): (0.7134, 11.998),
    ("Ferreñafe", 5): (0.7134, 11.998),
    ("Chongoyape", 1): (1.03, 0.4),
    ("Chongoyape", 2): (0.99, 0.8),
    ("Chongoyape", 3): (1.00, 0.0),
    ("Chongoyape", 4): (1.01, -0.3),
    ("Chongoyape", 5): (0.96, 0.9),
}

# Obtener coeficientes automáticamente
A, B = ecuaciones.get((zona, vuelo), (1.0, 0.0))  # Valor por defecto si no encuentra la combinación

# Subir la imagen
st.subheader("📂 Upload your thermal image (GeoTIFF)")
uploaded_file = st.file_uploader("Select your file:", type=["tif", "tiff"])

if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        profile = src.profile
        image = src.read(1).astype(np.float32)

    # Vista previa original
    st.subheader("🗾 Preview - Original Image")
    fig, ax = plt.subplots(figsize=(6, 4))
    vmin, vmax = np.percentile(image, [2, 98])
    ax.imshow(image, cmap='inferno', vmin=vmin, vmax=vmax)
    ax.axis('off')
    fig.colorbar(ax.images[0], ax=ax, label='Temperature')
    st.pyplot(fig)

    # Calibrar con los valores automáticos
    calibrated = A * image + B

    # Vista previa calibrada
    st.subheader("🗾 Preview - Calibrated Image")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    vmin2, vmax2 = np.percentile(calibrated, [2, 98])
    ax2.imshow(calibrated, cmap='inferno', vmin=vmin2, vmax=vmax2)
    ax2.axis('off')
    fig2.colorbar(ax2.images[0], ax=ax2, label='Calibrated Temperature')
    st.pyplot(fig2)

    # Guardar como GeoTIFF calibrado
    profile.update(dtype=rasterio.float32)
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(calibrated.astype(rasterio.float32), 1)
        mem_bytes = memfile.read()

    # Descargar
    st.subheader("💾 Download Calibrated Image")
    st.download_button("📥 Download Calibrated TIFF", data=mem_bytes,
                       file_name=f"{zona}_V{vuelo}_{hora}_calibrated.tif", mime="image/tiff")

else:
    st.info("Please upload a thermal image to begin.")
