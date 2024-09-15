import random
import streamlit as st
import numpy as np
import io
import base64
import wave

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

# Streamlit 앱 UI
st.markdown("<h3 style='text-align: center;'>Basic Chord Study</h3>", unsafe_allow_html=True)

# 태그 스타일 CSS 추가
st.markdown("""
<style>
.tag {
    display: inline-block;
    padding: 5px 10px;
    margin: 5px;
    border-radius: 20px;
    font-size: 18px;
    font-weight: bold;
    color: white;
}
.key-tag {
    background-color: #007bff;
}
.chord-tag {
    background-color: #28a745;
}
</style>
""", unsafe_allow_html=True)

# 전체 레이아웃을 3개의 열로 나누어 중앙 정렬
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # 새로고침 버튼
    if st.button('🔄', key='refresh'):
        st.session_state.key = random.choice(keys)
        st.session_state.chord_type = random.choice(chord_types)
        st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)
        st.experimental_rerun()

    # 키와 코드 유형을 태그로 표시
    st.markdown(f"""
    <div style='text-align: center;'>
        <span class='tag key-tag'>{st.session_state.key}</span>
        <span class='tag chord-tag'>{st.session_state.chord_type}</span>
    </div>
    """, unsafe_allow_html=True)

    # Inversion Arpeggio 체크박스
    include_inversions = st.checkbox('Inversion Arpeggio', key='include_inversions')

    # BPM 슬라이더 (더 작게 구현, 라벨 제거)
    bpm = st.slider('BPM', 60, 240, st.session_state.bpm, key='bpm', format="%d", step=1, label_visibility='collapsed')

    # 코드 재생 버튼
    if st.button('Play', key='play_chord'):
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