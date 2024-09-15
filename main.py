import random
import numpy as np
import sounddevice as sd
import streamlit as st
import time

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
    # 상행 진행
    for i in range(len(chord_notes)):
        inversion = chord_notes[i:] + [raise_octave(note) for note in chord_notes[:i]]
        inversions.append(inversion)
    
    # 상행 진행을 평탄화하고 역순으로 하행 진행 생성
    ascending = sum(inversions, [])
    descending = ascending[::-1]
    
    return ascending + descending

def raise_octave(note):
    note_name, octave = note[:-1], int(note[-1])
    return f"{note_name}{octave + 1}"

def note_to_freq(note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = ''.join([c for c in note if not c.isdigit()])
    octave = int(''.join([c for c in note if c.isdigit()]))
    base_freq = 261.6256  # C4의 주수
    note_index = notes.index(note_name)
    c_index = notes.index('C')
    half_steps = note_index - c_index + (octave - 4) * 12
    freq = base_freq * (2 ** (half_steps / 12))
    return freq

def play_chord(notes, duration=0.5, sample_rate=44100):
    bpm = st.session_state.bpm
    duration = 60 / bpm  # BPM에 따라 duration 조정
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    chord = np.zeros_like(t)
    for note in notes:
        freq = note_to_freq(note)
        chord += np.sin(2 * np.pi * freq * t)
    chord = chord / np.max(np.abs(chord))
    sd.play(chord, sample_rate)
    sd.wait()

def play_arpeggio(notes, duration=0.2, sample_rate=44100):
    bpm = st.session_state.bpm
    note_duration = 60 / bpm / 4  # 16분음표 기준으로 duration 조정
    for note in notes:
        play_chord([note], note_duration, sample_rate)
        time.sleep(note_duration * 0.9)  # 음표 사이에 짧은 간격 추가 (90% of note duration)

# 세션 상태 초기화
if 'key' not in st.session_state:
    st.session_state.key = random.choice(keys)
    st.session_state.chord_type = random.choice(chord_types)
    st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)

# 세션 상태 초기화
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

    # Inversion 체크박스
    include_inversions = st.checkbox('Inversion', key='include_inversions')

    # BPM 슬라이더 (더 작게 구현, 라벨 제거)
    st.slider('BPM', 60, 240, st.session_state.bpm, key='bpm', format="%d", step=1, label_visibility='collapsed')

    # 코드 재생 버튼
    if st.button('Play Chord', key='play_chord'):
        if include_inversions:
            chord_notes = generate_inversions(st.session_state.chord_notes)
            play_arpeggio(chord_notes)
        else:
            play_chord(st.session_state.chord_notes)

    # 약간의 공간 추가
    st.write("")
    st.write("")

    # 구성음 확인 토글
    show_notes = st.toggle('Show Notes', key='toggle_show_notes')

    # 구성음 표시
    if show_notes:
        notes_text = ' '.join([note[:-1] for note in st.session_state.chord_notes])
        st.write(f"Notes: {notes_text}")