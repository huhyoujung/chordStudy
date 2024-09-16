import streamlit as st
import base64
import random
import numpy as np
import io
import wave

# 이미지를 base64로 인코딩하는 함수
def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 로고 이미지를 base64로 인코딩
logo_base64 = img_to_base64("logo.png")

# 파비콘 설정
favicon_base64 = img_to_base64("logo.png")
st.set_page_config(page_title="ChordPlay", page_icon=f"data:image/png;base64,{favicon_base64}", layout="wide")

# CSS를 사용하여 폰트와 배경색 설정
st.markdown(f"""
    <style>
    @import url('https://timesnewerroman.com/TNR.css');
    .stApp {{
        background-color: white;
    }}
    body, .stButton>button, .stTextInput>div>div>input, .stSelectbox, .stSlider, p, h1, h2, h3, h4, h5, h6 {{
        font-family: 'Times Newer Roman', Times, serif !important;
    }}
    .key-style {{
        border: 2px solid black;
        color: black;
        background-color: white;
        padding: 10px 20px;
        border-radius: 50px;
        display: inline-block;
        font-size: 24px;
        font-weight: bold;
        font-family: 'Times Newer Roman', Times, serif !important;
        margin-right: 10px;
    }}
    .chord-type-style {{
        color: white;
        background-color: black;
        padding: 10px 20px;
        border-radius: 50px;
        display: inline-block;
        font-size: 24px;
        font-weight: bold;
        font-family: 'Times Newer Roman', Times, serif !important;
        margin-left: 10px;
    }}
    .center-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }}
    .stSlider [data-baseweb="slider"] div[role="slider"] div {{
        color: black !important;
    }}
    .stButton > button:hover {{
        border-color: black !important;
        color: black !important;
    }}
    .stCheckbox [data-baseweb="checkbox"] div[data-checked="true"] {{
        background-color: black !important;
    }}
    .stCheckbox [data-baseweb="checkbox"] div[data-focused="true"] {{
        border-color: black !important;
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.2) !important;
    }}
    .copyright {{
        position: fixed;
        left: 0;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 12px;
        color: #888;
        font-family: 'Times Newer Roman', Times, serif !important;
    }}
    .refresh-button-container {{
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }}
    .logo-img {{
        display: block;
        margin: 0 auto;
        width: 100px;
        height: auto;
    }}
    </style>
    
    <!-- 로고 이미지 추가 -->
    <img src="data:image/png;base64,{logo_base64}" class="logo-img">
    """, unsafe_allow_html=True)

keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
chord_types = ['Major', 'minor', 'sus4', 'aug', 'dim', 'Major7', 'minor7', 'Dominant7', 'Diminished7', 'Half Diminished7']

def generate_correct_answer(key, chord_type):
    base_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    intervals = {
        'Major': [0, 4, 7],
        'minor': [0, 3, 7],
        'sus4': [0, 5, 7],
        'aug': [0, 4, 8],
        'dim': [0, 3, 6],
        'Major7': [0, 4, 7, 11],
        'minor7': [0, 3, 7, 10],
        'Dominant7': [0, 4, 7, 10],
        'Diminished7': [0, 3, 6, 9],
        'Half Diminished7': [0, 3, 6, 10]
    }
    
    base_index = base_notes.index(key)
    chord_notes = []
    for interval in intervals[chord_type]:
        note_index = (base_index + interval) % 12
        octave = 4  # 기본 옥타브를 4로 설정
        if (base_index + interval) // 12 > 0:
            octave += 1
        note = f"{base_notes[note_index]}{octave}"
        chord_notes.append(note)
    return chord_notes

def generate_inversions(chord_notes):
    inversions = []
    for i in range(len(chord_notes)):
        inversion = chord_notes[i:] + [raise_octave(note) for note in chord_notes[:i]]
        inversions.append(inversion)
    
    ascending = sum(inversions, [])
    descending = ascending[::-1]
    
    return ascending + descending

def raise_octave(note):
    note_name, octave = note[:-1], int(note[-1])
    return f"{note_name}{octave + 1}"

def note_to_freq(note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = int(note[-1])
    note_name = note[:-1]
    semitones = notes.index(note_name)
    return 440 * (2 ** ((semitones - 9) / 12)) * (2 ** (octave - 4))

def create_sine_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * freq * t)

def create_chord_audio(frequencies, duration=1, sample_rate=44100):
    chord = np.zeros(int(sample_rate * duration))
    for freq in frequencies:
        chord += create_sine_wave(freq, duration, sample_rate)
    chord = chord / np.max(np.abs(chord))  # Normalize
    return (chord * 32767).astype(np.int16)

def create_arpeggio_audio(frequencies, bpm, sample_rate=44100):
    note_duration = 60 / bpm / 4  # 16분음표 기준
    arpeggio = np.array([], dtype=np.int16)
    for freq in frequencies:
        note = create_sine_wave(freq, note_duration, sample_rate)
        note = (note / np.max(np.abs(note)) * 32767).astype(np.int16)
        arpeggio = np.concatenate((arpeggio, note))
    return arpeggio

def get_audio_base64(audio_data, sample_rate=44100):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return base64.b64encode(buffer.getvalue()).decode()

# 세션 상태 초기화
if 'key' not in st.session_state:
    st.session_state.key = random.choice(keys)
    st.session_state.chord_type = random.choice(chord_types)
    st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)

if 'bpm' not in st.session_state:
    st.session_state.bpm = 120

# Streamlit 앱 UI (헤더 텍스트 변경 및 크기 축소)
st.markdown("<h3 style='text-align: center; font-family: \"Times Newer Roman\", Times, serif;'>ChordPlay</h3>", unsafe_allow_html=True)

# 전체 레이아웃을 3개의 열로 나누어 중앙 정렬
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 새로고침 버튼
    st.markdown('<div class="refresh-button-container">', unsafe_allow_html=True)
    if st.button('🔄', key='refresh'):
        st.session_state.key = random.choice(keys)
        st.session_state.chord_type = random.choice(chord_types)
        st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Key와 코드 유형 표시 부분
    st.markdown(f"""
    <div class="center-container">
        <div class="key-style">{st.session_state.key}</div>
        <div class="chord-type-style">{st.session_state.chord_type}</div>
    </div>
    """, unsafe_allow_html=True)

    # Inversion Arpeggio 체크박스
    include_inversions = st.checkbox('Inversion Arpeggio', key='include_inversions')

    # BPM 슬라이더 (더 작게 구현, 라벨 제거)
    bpm = st.slider('BPM', 60, 240, key='bpm', format="%d", step=1, label_visibility='collapsed')

    # 코드 재생 버튼
    if st.button('Answer Generation', key='play_chord'):
        frequencies = [note_to_freq(note) for note in st.session_state.chord_notes]
        if include_inversions:
            chord_notes = generate_inversions(st.session_state.chord_notes)
            frequencies = [note_to_freq(note) for note in chord_notes]
            audio_data = create_arpeggio_audio(frequencies, bpm)
        else:
            audio_data = create_chord_audio(frequencies)
        
        st.audio(audio_data, sample_rate=44100)

    # 구성음 확인 토글
    show_notes = st.toggle('Show Notes', key='toggle_show_notes')

    # 구성음 표시
    if show_notes:
        notes_text = ' '.join([note[:-1] for note in st.session_state.chord_notes])
        st.write(f"Notes: {notes_text}")

# 저작권 정보 추가
st.markdown('<div class="copyright">ⓒ 2024 Youjung Huh All Rights Reserved.</div>', unsafe_allow_html=True)