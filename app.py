# app.py
import io
import re
import time
from datetime import datetime
from typing import Tuple

import streamlit as st
from gtts import gTTS
from PIL import Image

# ---- Configuración general de la página ----
st.set_page_config(
    page_title="Texto → Audio (Multilenguaje)",
    page_icon="🔊",
    layout="centered"
)

# ---- Encabezado y branding ----
st.title("🔊 Conversión de Texto a Audio – Multilenguaje")
st.caption("Creación de Interfaces Multimodales · Texto→Audio con Streamlit + gTTS")

# Imagen opcional (no falla si no existe)
try:
    image = Image.open("gato_raton.png")
    st.image(image, width=350, caption="Demo: Fábula breve")
except Exception:
    st.info("Puedes agregar una imagen local llamada **gato_raton.png** para mostrarla aquí (opcional).")

# ---- Sidebar: instrucciones y controles globales ----
with st.sidebar:
    st.subheader("Instrucciones")
    st.markdown(
        "- Escribe o pega tu texto.\n"
        "- Elige idioma, acento (tld) y velocidad.\n"
        "- Haz clic en **Generar audio**.\n"
        "- Reproduce o descarga el MP3."
    )
    st.markdown("**Sugerencia:** Textos con puntuación (.,;:!) generan pausas más naturales.")

    # Velocidad (lento/normal)
    slow_mode = st.toggle("Hablar más lento", value=False, help="Activa un ritmo de habla más pausado.")

# ---- Texto de ejemplo (fábula) y utilidades ----
KAFKA_TEXT = (
    "¡Ay! —dijo el ratón—. El mundo se hace cada día más pequeño. Al principio era tan grande que le tenía miedo. "
    "Corría y corría, y me alegraba ver esos muros, a diestra y siniestra, en la distancia. "
    "Pero esas paredes se estrechan tan rápido que me encuentro en el último cuarto y, en el rincón, está la trampa "
    "sobre la cual debo pasar. "
    "—Todo lo que debes hacer es cambiar de rumbo —dijo el gato… y se lo comió. "
    "Franz Kafka."
)

with st.expander("📚 Fábula de ejemplo (Kafka)"):
    st.write(KAFKA_TEXT)
    if st.button("Copiar fábula al editor"):
        st.session_state["texto_editor"] = KAFKA_TEXT

# ---- Selección de idioma y acento (tld) ----
st.subheader("Parámetros de voz")

# Idiomas comunes soportados por gTTS
LANG_OPTIONS = {
    "Español": "es",
    "English": "en",
    "Português": "pt",
    "Français": "fr",
    "Italiano": "it",
    "Deutsch": "de",
    "日本語 (Japanese)": "ja"
}
lang_label = st.selectbox("Idioma", list(LANG_OPTIONS.keys()), index=0)
lang_code = LANG_OPTIONS[lang_label]

# Variantes de dominio para matizar acento (no todos impactan todos los idiomas)
# Escoge un subconjunto probado; 'com' suele ser buena por defecto.
TLD_OPTIONS = {
    "Neutro (com)": "com",
    "España (es)": "es",
    "México (com.mx)": "com.mx",
    "Colombia (com.co)": "com.co",
    "Argentina (com.ar)": "com.ar",
    "Estados Unidos (com)": "com",
    "Reino Unido (co.uk)": "co.uk",
    "Brasil (com.br)": "com.br",
}
tld_label = st.selectbox("Acento / región (tld)", list(TLD_OPTIONS.keys()), index=0)
tld_value = TLD_OPTIONS[tld_label]

# ---- Editor de texto ----
st.subheader("Texto a convertir")
default_text = st.session_state.get("texto_editor", "Hola, esta es mi interfaz de Texto a Audio con varios idiomas.")
text = st.text_area("Ingresa el texto", value=default_text, height=180, max_chars=8000, help="Admite acentos, eñes y signos ¡¿.")

# Nombre de archivo sugerido
filename_input = st.text_input("Nombre de archivo (opcional, sin extensión)", value="audio")

# ---- Utilidades ----
def sanitize_filename(name: str) -> str:
    """Limpia el nombre de archivo; quita caracteres no válidos y recorta longitud."""
    name = name.strip() or "audio"
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name[:50]

def make_unique_basename(base: str) -> str:
    """Añade timestamp para evitar colisiones."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{ts}"

def synthesize_gtts(txt: str, lang: str, tld: str, slow: bool) -> Tuple[bytes, str]:
    """
    Genera audio con gTTS y devuelve (bytes_mp3, nombre_archivo_sugerido).
    Usa buffer en memoria (no escribe a disco).
    """
    # gTTS: si no pasas tld, usa dominio por defecto; aquí lo exponemos para matiz regional
    tts = gTTS(text=txt, lang=lang, tld=tld, slow=slow)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    # Nombre sugerido
    base = sanitize_filename(filename_input or (txt[:20] if txt else "audio"))
    unique_name = make_unique_basename(base)
    return buffer.read(), f"{unique_name}.mp3"

# ---- Acción principal ----
col1, col2 = st.columns([1, 1])
with col1:
    generate = st.button("🎙️ Generar audio", type="primary")
with col2:
    clear = st.button("🧹 Limpiar")

if clear:
    st.session_state.pop("texto_editor", None)
    st.experimental_rerun()

if generate:
    if not text or not text.strip():
        st.warning("Por favor, escribe un texto para convertir.")
    else:
        with st.spinner("Generando audio..."):
            try:
                start = time.time()
                audio_bytes, suggested_name = synthesize_gtts(text.strip(), lang_code, tld_value, slow_mode)
                elapsed = time.time() - start
                st.success(f"¡Listo! ({elapsed:.2f} s)")
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    "⬇️ Descargar MP3",
                    data=audio_bytes,
                    file_name=suggested_name,
                    mime="audio/mpeg",
                    use_container_width=True
                )
            except Exception as e:
                st.error("No se pudo generar el audio. Revisa tu conexión e intenta de nuevo.")
                st.caption(f"Detalle técnico (solo para depuración): {e}")

# ---- Notas técnicas ----
st.divider()
with st.expander("ℹ️ Notas técnicas"):
    st.markdown(
        """
- Motor: **gTTS** (Google Text-to-Speech) vía librería de Python.
- **Idiomas:** Español, Inglés, Portugués, Francés, Italiano, Alemán y Japonés.
- **Acento (tld):** permite matizar la variante (p. ej., `com`, `com.mx`, `es`, `com.co`). El efecto puede variar según idioma.
- **Velocidad:** alterna modo lento/normal.
- **Privacidad:** el audio se construye en memoria (no se guarda en disco del servidor).
- **Descarga:** se ofrece un archivo `.mp3` con nombre único (timestamp).
"""
    )
    
