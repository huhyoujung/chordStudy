import random
import numpy as np
import sounddevice as sd
import streamlit as st

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
    
    # 상승
    for i in range(len(chord_notes)):
        inversion = chord_notes[i:] + [raise_octave(note) for note in chord_notes[:i]]
        inversions.append(inversion)
    
    # 상승 리스트를 평탄화
    ascending = [note for inversion in inversions for note in inversion]
    
    # 하강 (평탄화된 상승의 역순)
    descending = ascending[::-1]
    
    # 상승과 하강을 합침
    return ascending + descending

def raise_octave(note):
    note_name, octave = note[:-1], int(note[-1])
    return f"{note_name}{octave + 1}"

def lower_octave(note):
    note_name, octave = note[:-1], int(note[-1])
    return f"{note_name}{octave - 1}"

def note_to_freq(note):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = note[:-1]
    octave = int(note[-1])
    base_freq = 261.6256  # C4의 주파수
    note_index = notes.index(note_name)
    c_index = notes.index('C')
    half_steps = note_index - c_index + (octave - 4) * 12
    freq = base_freq * (2 ** (half_steps / 12))
    return freq

def play_chord(frequencies, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    chord = np.zeros_like(t)
    for freq in frequencies:
        chord += np.sin(2 * np.pi * freq * t)
    chord = chord / np.max(np.abs(chord))
    sd.play(chord, sample_rate)
    sd.wait()

# Streamlit 앱 구성
st.title('화성학 학습 앱')

if 'key' not in st.session_state:
    st.session_state.key = random.choice(keys)
    st.session_state.chord_type = random.choice(chord_types)
    st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)

st.write(f"키: {st.session_state.key}")
st.write(f"코드 유형: {st.session_state.chord_type}")

if st.button('새로운 문제'):
    st.session_state.key = random.choice(keys)
    st.session_state.chord_type = random.choice(chord_types)
    st.session_state.chord_notes = generate_correct_answer(st.session_state.key, st.session_state.chord_type)
    st.experimental_rerun()

if st.button('코드 재생'):
    frequencies = [note_to_freq(note) for note in st.session_state.chord_notes]
    play_chord(frequencies, 1.0)

show_notes = st.button('구성음 확인')
if show_notes:
    st.write(f"구성음: {' '.join([note[:-1] for note in st.session_state.chord_notes])}")

include_inversions = st.checkbox('자리바꿈 포함')

bpm = st.slider('BPM', 60, 240, 120)

if st.button('전체 진행 재생'):
    if include_inversions:
        play_notes = generate_inversions(st.session_state.chord_notes)
    else:
        play_notes = st.session_state.chord_notes
    
    frequencies = [note_to_freq(note) for note in play_notes]
    note_duration = 60 / bpm
    
    for freq in frequencies:
        play_chord([freq], note_duration)