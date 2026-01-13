import streamlit as st
from streamlit_mic_recorder import mic_recorder
import ollama
import json
import io
import os
import whisper
import tempfile
import asyncio
import edge_tts

st.set_page_config(page_title="Voice-to-Voice", layout="wide")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama-api:11434")
client = ollama.Client(host=OLLAMA_HOST)

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

@st.cache_data
def load_knowledge_base():
    try:
        with open('data_siswa.json', 'r') as f:
            return json.dumps(json.load(f))
    except FileNotFoundError:
        return "{}"

stt_model = load_whisper_model()
data_context = load_knowledge_base()

async def generate_edge_tts(text, voice, rate):
    speed = f"+{rate}%" if rate >= 0 else f"{rate}%"
    communicate = edge_tts.Communicate(text, voice, rate=speed)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

with st.sidebar:
    st.header("Model Settings")
    selected_model = st.selectbox("Model", ["llama3.2"])
    temp = st.slider("Temperature", 0.0, 2.0, 0.0, 0.1)
    max_tokens = st.slider("Output token limit", 1, 8192, 512)
    top_p = st.slider("Top-P", 0.0, 1.0, 0.9, 0.05)
    
    st.divider()
    st.header("Voice Settings")
    
    voice_option = st.selectbox(
        "Pilih Suara",
        ["id-ID-ArdiNeural (Pria)", "id-ID-GadisNeural (Wanita)"],
        index=1
    )
    selected_voice = voice_option.split(" ")[0]
    
    voice_speed = st.slider("Kecepatan Suara (%)", -50, 100, 25, step=5)
    
    st.divider()
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Voice-to-Voice")
st.write("Tanya data siswa dengan suara yang lebih natural dan cepat.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

audio = mic_recorder(start_prompt="Mulai Bicara 🎤", stop_prompt="Selesai & Proses ⏹️", key='recorder')

if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio['bytes'])
        tmp_path = tmp_file.name

    try:
        with st.spinner("Menerjemahkan suara Anda..."):
            result = stt_model.transcribe(tmp_path, fp16=False, language='id')
            user_query = result['text'].strip()

        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Berpikir..."):
                    response = client.chat(
                        model=selected_model,
                        messages=[
                            {'role': 'system', 'content': f'Anda asisten data siswa. Jawab HANYA berdasarkan data ini: {data_context}.'},
                            {'role': 'user', 'content': user_query}
                        ],
                        options={'temperature': temp, 'num_predict': max_tokens, 'top_p': top_p}
                    )
                    answer = response['message']['content']
                    st.write(answer)

                    with st.spinner("Menghasilkan suara..."):
                        audio_bytes = asyncio.run(generate_edge_tts(answer, selected_voice, voice_speed))
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

                    st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)