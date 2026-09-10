import streamlit as st
import fitz  # PyMuPDF
import io

# Configuración visual: Fondo Negro (Modo Oscuro)
st.set_page_config(page_title="Color PDF Optimizer", page_icon="🎨")

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #28a745;
        color: white;
        border-radius: 10px;
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #218838;
        border: 1px solid #ffffff;
    }
    p, h1, h2, h3, span, label {
        color: #ffffff !important;
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #1a1c23;
        border: 1px solid #444;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 Compresor Pro: Color y Calidad")
st.write("Objetivo: Mantener el peso entre **60 KB y 100 KB** con colores vivos.")

archivo = st.file_uploader("Sube tu PDF", type="pdf")

if archivo:
    datos_originales = archivo.getvalue()
    peso_inicial = len(datos_originales) / 1024
    st.write(f"Peso inicial: **{peso_inicial:.2f} KB**")

    if st.button("🚀 Optimizar PDF a Color"):
        with st.spinner("Calculando compresión ideal..."):
            doc_original = fitz.open(stream=datos_originales, filetype="pdf")
            
            # Lógica para no bajar de 60 KB: 
            # Si el original es pequeño, usamos calidad alta.
            # Si el original es grande, bajamos calidad para no pasar el mega.
            calidad_ideal = 45 if peso_inicial < 300 else 25
            matriz_ideal = 1.1 if peso_inicial < 300 else 0.9

            nuevo_pdf = fitz.open()

            for pagina in doc_original:
                # Mantenemos RGB para que sea a Color
                pix = pagina.get_pixmap(matrix=fitz.Matrix(matriz_ideal, matriz_ideal), colorspace=fitz.csRGB)
                
                # Re-comprimimos con la calidad calculada
                img_bytes = pix.tobytes("jpg", jpg_quality=calidad_ideal)
                
                nueva_pag = nuevo_pdf.new_page(width=pagina.rect.width, 
                                               height=pagina.rect.height)
                
                nueva_pag.insert_image(pagina.rect, stream=img_bytes)
                pix = None

            # Guardado final
            buffer_salida = io.BytesIO()
            nuevo_pdf.save(buffer_salida, garbage=4, deflate=True, clean=True)
            
            datos_finales = buffer_salida.getvalue()
            peso_final = len(datos_finales) / 1024
            
            # --- Validaciones de peso ---
            if 60 <= peso_final <= 100:
                st.success(f" ¡Objetivo logrado! Peso: **{peso_final:.2f} KB** (Color nítido)")
            elif peso_final < 60:
                st.warning(f" Peso: **{peso_final:.2f} KB**. El archivo es muy simple, pero mantiene el color.")
            else:
                st.info(f" Optimizado: **{peso_final:.2f} KB** (Por debajo de 1 MB)")

            st.download_button(
                label="📥 Descargar Resultado Final",
                data=datos_finales,
                file_name=f"optimizado_color_{archivo.name}",
                mime="application/pdf"
            )
            
            doc_original.close()
            nuevo_pdf.close()
