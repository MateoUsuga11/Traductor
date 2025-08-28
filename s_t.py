import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

st.title("TRADUCTOR.")
st.subheader("Escucho lo que quieres traducir.")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    st.write(
        "Presiona el botón, cuando escuches la señal "
        "habla lo que quieres traducir, luego selecciona "
        "la configuración de lenguaje que necesites."
    )

st.write("Toca el Botón y habla lo que quieres traducir")

# --- Botón de reconocimiento de voz ---
stt_button = Button(label=" Escuchar  🎤", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# --- Función para mapear idiomas ---
def map_language(lang):
    if lang == "Inglés":
        return "en"
    elif lang == "Español":
        return "es"
    elif lang == "Bengali":
        return "bn"
    elif lang == "Coreano":
        return "ko"
    elif lang == "Mandarín":
        return "zh-cn"
    elif lang == "Japonés":
        return "ja"
    elif lang == "Italiano":
        return "it"
    elif lang == "Francés":
        return "fr"
    elif lang == "Alemán":
        return "de"
    else:
        return "en"  # fallback

if result and "GET_TEXT" in result:
    st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass

    st.title("Texto a Audio")
    translator = Translator()

    text = str(result.get("GET_TEXT"))

    idiomas = ["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés", "Italiano", "Francés", "Alemán"]

    in_lang = st.selectbox("Selecciona el lenguaje de Entrada", idiomas)
    out_lang = st.selectbox("Selecciona el lenguaje de salida", idiomas)

    input_language = map_language(in_lang)
    output_language = map_language(out_lang)

    # --- Acentos ---
    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )

    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "Español":
        tld = "com.mx"
    elif english_accent == "Reino Unido":
        tld = "co.uk"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Irlanda":
        tld = "ie"
    elif english_accent == "Sudáfrica":
        tld = "co.za"

    # --- Función de traducción y TTS ---
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20].replace(" ", "_")
        except:
            my_file_name = "audio"
        file_path = f"temp/{my_file_name}.mp3"
        tts.save(file_path)
        return file_path, trans_text

    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("Convertir"):
        file_path, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(file_path, "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## Texto de salida:")
            st.write(f"{output_text}")

    # --- Limpieza de archivos viejos ---
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)



        
    


