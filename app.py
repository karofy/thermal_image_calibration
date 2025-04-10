import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile

st.set_page_config(page_title="Thermal Calibration", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
        /* Cargar fuente de Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&display=swap');

        /* Fondo con degradado */
        body {
            background: linear-gradient(to bottom right, #1e3c72, #2a5298);
            color: white;
            font-family: 'PT Serif', serif; /* Cambié la fuente aquí */
        }

        /* Títulos centrados y estilizados */
        h1 {
            text-align: center;
            color: #ffcc00;
            font-size: 40px;
            font-family: 'PT Serif', serif; /* Cambié la fuente aquí también */
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

        /* Inputs */
        .stNumberInput input {
            background-color: #f0f0f0;
            color: #333;
            font-family: 'PT Serif', serif;
        }

        /* Subtítulos */
        h2, h3, .stMarkdown {
            color: #f0f0f0;
            font-family: 'PT Serif', serif;
        }

        /* Cuadros de carga */
        .stFileUploader {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align: center; color: #ff6600;'>🌡️ Thermal Image Calibration</h1>", unsafe_allow_html=True)
st.write("This app allows you to upload a thermal orthomosaic, apply a **calibration equation (A × value + B)**, and visualize the results.")

# Subir la imagen
st.subheader("📂 1. Upload your thermal image (GeoTIFF)")
uploaded_file = st.file_uploader("Select your file:", type=["tif", "tiff"])

# Parámetros de calibración
st.subheader("⚙️ 2. Enter calibration coefficients")
A = st.number_input("🔢 Coefficient A (multiplier)", format="%.5f", value=1.00000)
B = st.number_input("➕ Coefficient B (offset)", format="%.5f", value=0.00000)

if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        profile = src.profile
        image = src.read(1).astype(np.float32)  # Leer banda 1  
    
    # Vista previa original
    st.subheader("🖼️ Preview - Original Image")
    fig, ax = plt.subplots(figsize=(6, 4))
    vmin, vmax = np.percentile(image, [2, 98])
    img_show = ax.imshow(image, cmap='inferno', vmin=vmin, vmax=vmax)
    ax.axis('off')
    fig.colorbar(img_show, ax=ax, label='Temperature')
    st.pyplot(fig)

    # Aplicar calibración
    calibrated = A * image + B

    # Vista previa calibrada
    st.subheader("🖼️ 3. Preview - Calibrated Image")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    vmin2, vmax2 = np.percentile(calibrated, [2, 98])
    calibrated_show = ax2.imshow(calibrated, cmap='inferno', vmin=vmin2, vmax=vmax2)
    ax2.axis('off')
    fig2.colorbar(calibrated_show, ax=ax2, label='Calibrated Temperature')
    st.pyplot(fig2)

    # Guardar como GeoTIFF calibrado
    profile.update(dtype=rasterio.float32)
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(calibrated.astype(rasterio.float32), 1)
        mem_bytes = memfile.read()

    # Descargar resultado
    st.subheader("💾 4. Download Calibrated Image")
    st.download_button("📥 Download Calibrated TIFF", data=mem_bytes,
                       file_name="calibrated_image.tif", mime="image/tiff")

else:
    st.info("Please upload a thermal image to begin.")