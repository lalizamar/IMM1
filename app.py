# app.py
import io, re, time, base64
from datetime import datetime
from typing import Tuple
import streamlit as st
from gtts import gTTS
from PIL import Image

# ---------- CONFIG ----------
st.set_page_config(
    page_title="💗 Texto → Audio Cute",
    page_icon="🧸",
    layout="centered"
)

# ---------- THEME PALETTES ----------
PALETTES = {
    "Rosa Sakura 🌸": {
        "--bg": "linear-gradient(180deg,#fff7fb 0%, #ffe7f1 100%)",
        "--card": "#ffffffcc",
        "--accent": "#ff77a9",
        "--accent-2": "#ffbfd5",
        "--text": "#5b3b4a",
        "--muted": "#8a5e6e",
        "--shadow": "0 10px 30px rgba(255,119,169,0.25)",
    },
    "Lavanda 💜": {
        "--bg": "linear-gradient(180deg,#fbf7ff 0%, #efe7ff 100%)",
        "--card": "#ffffffcc",
        "--accent": "#9b6bff",
        "--accent-2": "#d9c7ff",
        "--text": "#3f3356",
        "--muted": "#6a5a8b",
        "--shadow": "0 10px 30px rgba(155,107,255,0.25)",
    },
    "Aqua Menta 🫧": {
        "--bg": "linear-gradient(180deg,#f4fffd 0%, #e5fff7 100%)",
        "--card": "#ffffffcc",
        "--accent": "#39c6b3",
        "--accent-2": "#bdf1e9",
        "--text": "#244a47",
        "--muted": "#447c77",
        "--shadow": "0 10px 30px rgba(57,198,179,0.22)",
    },
    "Durazno 🍑": {
        "--bg": "linear-gradient(180deg,#fff8f3 0%, #ffe4cf 100%)",
        "--card": "#ffffffcc",
        "--accent": "#ff9b6a",
        "--accent-2": "#ffd1bd",
        "--text": "#5a3b2e",
        "--muted": "#8a6556",
        "--shadow": "0 10px 30px rgba(255,155,106,0.22)",
    },
}

# ---------- SIDEBAR CONTROLS ----------
with st.sidebar:
    st.markdown("## 🎀 Personaliza el estilo")
    theme_name = st.selectbox("Paleta kawaii", list(PALETTES.keys()), index=0)
    show_confetti = st.toggle("✨ Confetti al generar", value=True)
    st.markdown("---")
    st.markdown("## 🖼️ Imagen")
    img_file = st.file_uploader("Sube tu imagen (PNG/JPG)", type=["png", "jpg", "jpeg"])
    st.caption("Si no subes una imagen, se usa una ilustración kawaii por defecto 💞")
    st.markdown("---")
    st.markdown("## 💡 Tip")
    st.write("Usa puntuación (.,;:!?) para pausas naturales. Textos de 1–3 párrafos suenan mejor.")

# ---------- APPLY THEME (CSS) ----------
palette = PALETTES[theme_name]
css = f"""
<style>
:root {{
  --accent: {palette['--accent']};
  --accent-2: {palette['--accent-2']};
  --text: {palette['--text']};
  --muted: {palette['--muted']};
}}
html, body, [data-testid="stAppViewContainer"] {{
  background: {palette['--bg']} !important;
}}
section.main > div:has(> .block-container) {{
  padding-top: 1.2rem !important;
}}
.block-container {{
  padding: 1.5rem 1.2rem;
}}
/* Card */
.cute-card {{
  background: {palette['--card']};
  border: 2px solid var(--accent-2);
  box-shadow: {palette['--shadow']};
  border-radius: 24px;
  padding: 1.1rem 1.2rem;
  backdrop-filter: blur(6px);
}}
/* Titles */
h1, h2, h3, label, .stMarkdown p {{
  color: var(--text) !important;
}}
/* Buttons */
div.stButton > button {{
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 1000px;
  padding: 0.6rem 1rem;
  font-weight: 700;
  box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}}
div.stButton > button:hover {{
  filter: brightness(1.03);
  transform: translateY(-1px);
}}
/* Inputs */
.stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
  border-radius: 14px !important;
  border: 2px solid var(--accent-2) !important;
}}
/* Chips */
.chip {{
  display:inline-flex; align-items:center; gap:.4rem;
  padding:.35rem .7rem; border-radius:999px;
  background: var(--accent-2); color: var(--text); font-weight:600; font-size:.85rem;
}}
/* Cute divider */
.cute-divider {{
  width: 100%; height: 12px; border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  opacity:.6; margin: .8rem 0 1.2rem 0;
}}
/* Audio */
.stAudio audio {{
  width: 100% !important;
  border-radius: 12px; outline: none;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------- HEADER ----------
colA, colB = st.columns([1,1], vertical_alignment="center")
with colA:
    st.markdown("### 🧸 **Texto → Audio Cute**")
    st.caption("Creación de Interfaces Multimodales · Streamlit + gTTS")
    st.markdown('<div class="chip">🌸 Tierno</div> <div class="chip">💞 Pastel</div> <div class="chip">🎧 TTS</div>', unsafe_allow_html=True)
with colB:
    # Show uploaded image or fallback to kawaii SVG
    if img_file:
        try:
            img = Image.open(img_file)
            st.image(img, caption="Tu imagen", use_column_width=True)
        except Exception:
            st.info("No se pudo abrir la imagen. Se muestra la ilustración por defecto.")
            img_file = None

    if not img_file:
        # Simple SVG kawaii (corazones)
        svg = """
        <svg viewBox="0 0 300 140" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g" x1="0" x2="1">
              <stop stop-color="#FFC2D4"/>
              <stop offset="1" stop-color="#FF8FB3"/>
            </linearGradient>
          </defs>
          <rect x="0" y="0" width="300" height="140" rx="22" fill="url(#g)" opacity="0.35"/>
          <g transform="translate(30,25)">
            <path d="M40 30c0-11 9-20 20-20 7 0 13 3 17 8 4-5 10-8 17-8 11 0 20 9 20 20 0 26-37 36-37 36S40 56 40 30z" fill="#ff6fa0"/>
          </g>
          <g transform="translate(150,50) scale(0.7)">
            <path d="M40 30c0-11 9-20 20-20 7 0 13 3 17 8 4-5 10-8 17-8 11 0 20 9 20 20 0 26-37 36-37 36S40 56 40 30z" fill="#ff9bc0"/>
          </g>
          <text x="150" y="120" text-anchor="middle" font-size="16" fill="#5b3b4a" font-family="Arial">Voces suaves para tus palabras</text>
        </svg>
        """
        st.markdown(f'<div class="cute-card">{svg}</div>', unsafe_allow_html=True)

st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)

# ---------- SAMPLE TEXT ----------
KAFKA_TEXT = (
    "¡Ay! —dijo el ratón—. El mundo se hace cada día más pequeño. Al principio era tan grande que le tenía miedo. "
    "Corría y corría, y me alegraba ver esos muros en la distancia. Pero esas paredes se estrechan tan rápido que me "
    "encuentro en el último cuarto y, en el rincón, está la trampa. —Todo lo que debes hacer es cambiar de rumbo —dijo el gato… y se lo comió. "
    "Franz Kafka."
)

with st.expander("📚 Texto de ejemplo (Kafka)"):
    st.write(KAFKA_TEXT)
    if st.button("💗 Copiar al editor"):
        st.session_state["texto_editor"] = KAFKA_TEXT
        st.success("¡Listo! Se copió al editor ✨")

# ---------- VOICE PARAMS ----------
st.markdown("#### 🎀 Parámetros de voz")
with st.container():
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        LANG_OPTIONS = {
            "Español": "es",
            "English": "en",
            "Português": "pt",
            "Français": "fr",
            "Italiano": "it",
            "Deutsch": "de",
            "日本語 (Japanese)": "ja",
            "한국어 (Korean)": "ko"
        }
        lang_label = st.selectbox("Idioma", list(LANG_OPTIONS.keys()), index=0)
        lang_code = LANG_OPTIONS[lang_label]
    with c2:
        TLD_OPTIONS = {
            "Neutro (com)": "com",
            "España (es)": "es",
            "México (com.mx)": "com.mx",
            "Colombia (com.co)": "com.co",
            "Argentina (com.ar)": "com.ar",
            "EE.UU. (com)": "com",
            "Reino Unido (co.uk)": "co.uk",
            "Brasil (com.br)": "com.br",
            "Japón (co.jp)": "co.jp"
        }
        tld_label = st.selectbox("Acento / región (tld)", list(TLD_OPTIONS.keys()), index=0)
        tld_value = TLD_OPTIONS[tld_label]
    with c3:
        slow_mode = st.toggle("🕊️ Hablar más lento", value=False)

# ---------- TEXT AREA ----------
st.markdown("#### 📝 Texto a convertir")
default_text = st.session_state.get("texto_editor", "Hola, esta es mi interfaz de Texto a Audio suave y kawaii.")
text = st.text_area("Escribe aquí", value=default_text, height=180, max_chars=8000, help="Acentos, eñes y símbolos ¡¿ funcionan.")

# ---------- FILENAME ----------
def sanitize_filename(name: str) -> str:
    name = (name or "").strip() or "audio"
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name[:50]

def make_unique_basename(base: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{ts}"

filename_input = st.text_input("Nombre de archivo (sin extensión)", value="mi_audio_cute")
base_name = sanitize_filename(filename_input)

# ---------- TTS ----------
def synthesize_gtts(txt: str, lang: str, tld: str, slow: bool) -> Tuple[bytes, str]:
    tts = gTTS(text=txt, lang=lang, tld=tld, slow=slow)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    unique = make_unique_basename(base_name if base_name else "audio")
    return buffer.read(), f"{unique}.mp3"

st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)

# ---------- ACTIONS ----------
a1, a2 = st.columns([1,1])
with a1:
    generate = st.button("🎙️ Generar audio", type="primary")
with a2:
    clear = st.button("🧼 Limpiar editor")

if clear:
    st.session_state.pop("texto_editor", None)
    st.experimental_rerun()

if generate:
    if not text or not text.strip():
        st.warning("Por favor, escribe un texto para convertir 🫶")
    else:
        with st.spinner("Tejiendo una voz dulce… 💞"):
            try:
                start = time.time()
                audio_bytes, suggested_name = synthesize_gtts(text.strip(), lang_code, tld_value, slow_mode)
                elapsed = time.time() - start
                st.success(f"¡Listo! ({elapsed:.2f} s) Tu audio está abajo ⬇️")
                if show_confetti:
                    st.balloons()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    "⬇️ Descargar MP3",
                    data=audio_bytes,
                    file_name=suggested_name,
                    mime="audio/mpeg",
                    use_container_width=True
                )
            except Exception as e:
                st.error("No se pudo generar el audio. Intenta de nuevo.")
                st.caption(f"Detalle técnico: {e}")

# ---------- FOOTNOTE ----------
st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown(
        f"""
<div class="cute-card">
  <b>ℹ️ Notas técnicas</b><br>
  • Motor: <b>gTTS</b> (Google Text-to-Speech).<br>
  • Idiomas: ES, EN, PT, FR, IT, DE, JA, KO (según disponibilidad gTTS).<br>
  • Acento (tld): variantes regionales (p. ej., <code>com</code>, <code>com.mx</code>, <code>es</code>, <code>com.co</code>).<br>
  • Velocidad: normal/lento.<br>
  • Privacidad: el audio se genera en memoria, no se guarda en disco del servidor.<br>
  • Descarga: archivo <code>.mp3</code> con timestamp para evitar colisiones.<br>
</div>
""",
        unsafe_allow_html=True
    )
