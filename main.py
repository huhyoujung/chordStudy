import random
import tkinter as tk
from tkinter import messagebox, Scale
import pygame
import numpy as np
import time
import threading
import sys

keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
chord_types = ['Major', 'minor', 'sus4', 'aug', 'dim', 'Major7', 'minor7', 'Dominant7', 'Diminished7', 'Half Diminished7']

class HarmonyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("화성학 학습 앱")
        
        self.pygame_initialized = False
        self.initialize_pygame()
        
        self.key = tk.StringVar()
        self.chord_type = tk.StringVar()
        self.chord_notes = tk.StringVar()
        
        tk.Button(master, text="새로운 문제", command=self.generate_question).pack()
        
        self.question_frame = tk.Frame(master)
        self.question_frame.pack()
        
        tk.Label(self.question_frame, textvariable=self.key).pack()
        tk.Label(self.question_frame, textvariable=self.chord_type).pack()
        
        self.chord_notes_label = tk.Label(self.question_frame, textvariable=self.chord_notes)
        self.chord_notes_label.pack()
        self.chord_notes_label.pack_forget()  # 초기에는 숨김
        
        self.check_button = tk.Button(self.question_frame, text="구성음 확인")
        self.check_button.pack()
        self.check_button.bind('<ButtonPress>', self.show_chord_notes)
        self.check_button.bind('<ButtonRelease>', self.hide_chord_notes)
        
        tk.Button(self.question_frame, text="코드 재생", command=self.play_chord).pack()
        
        self.inversion_var = tk.BooleanVar()
        self.inversion_check = tk.Checkbutton(self.question_frame, text="자리바꿈 포함", variable=self.inversion_var, command=self.update_chord_notes)
        self.inversion_check.pack()
        
        self.bpm = tk.IntVar(value=120)  # 기본 BPM 값을 120으로 설정
        self.bpm_slider = Scale(self.question_frame, from_=60, to=240, orient=tk.HORIZONTAL, 
                                label="BPM", variable=self.bpm, command=self.update_bpm)
        self.bpm_slider.pack()
        
        self.generate_question()
    
    def initialize_pygame(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)
            pygame.mixer.set_num_channels(16)  # 채널 수 증가
            self.pygame_initialized = True
        except Exception as e:
            print(f"pygame 초기화 중 오류 발: {e}")
            messagebox.showerror("오류", f"오디오 시스템을 초기화할 수 없습니다: {e}")

    def generate_question(self):
        self.key.set(f"키: {random.choice(keys)}")
        self.chord_type.set(f"코드 유형: {random.choice(chord_types)}")
        self.update_chord_notes()
    
    def update_chord_notes(self):
        key = self.key.get().split(": ")[1]
        chord_type = self.chord_type.get().split(": ")[1]
        chord_notes = self.generate_correct_answer(key, chord_type)
        simplified_notes = [note[:-1] for note in chord_notes]  # 옥타 정보 제거
        self.chord_notes.set(f"구성음: {' '.join(simplified_notes)}")

    def show_chord_notes(self, event):
        self.chord_notes_label.pack()

    def hide_chord_notes(self, event):
        self.chord_notes_label.pack_forget()

    def play_chord(self):
        if not self.pygame_initialized:
            messagebox.showerror("오류", "오디오 시스템이 초기화되지 않았습니다.")
            return
        threading.Thread(target=self._play_chord).start()

    def update_bpm(self, value):
        self.bpm.set(int(value))

    def _play_chord(self):
        try:
            key = self.key.get().split(": ")[1]
            chord_type = self.chord_type.get().split(": ")[1]
            chord_notes = self.generate_correct_answer(key, chord_type)
            
            if self.inversion_var.get():
                play_notes = self.generate_inversions(chord_notes)
            else:
                play_notes = chord_notes
            
            frequencies = [self.note_to_freq(note) for note in play_notes]
            
            note_duration = 60 / self.bpm.get()  # BPM에 따른 4분음표 길이 계산
            
            print("재생되는 음 목록:")
            for note in play_notes:
                print(note, end=" ")
            print("\n")
            
            # 상승 진행
            for freq in frequencies[:len(chord_notes) * len(chord_notes)]:
                self.play_single_note(freq, note_duration)
            
            # 하강 진행
            for freq in frequencies[len(chord_notes) * len(chord_notes):]:
                self.play_single_note(freq, note_duration)
            
            # 전체 화음 재생
            self.play_full_chord([self.note_to_freq(note) for note in chord_notes], note_duration * 2)
        except Exception as e:
            print(f"코드 재생 중 오류 발생: {e}")
            messagebox.showerror("오류", f"코드 재생 중 문제가 발생했습니다: {e}")

    def play_single_note(self, freq, duration):
        if not pygame.mixer.get_init():
            print("믹서가 초기화되지 않았습니다.")
            return
        try:
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(2 * np.pi * freq * t)
            note = (note * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(note)
            sound.play()
            pygame.time.wait(int(duration * 1000))
        except Exception as e:
            print(f"음 재생 중 오류 발생: {e}")

    def play_full_chord(self, frequencies, duration):
        if not pygame.mixer.get_init():
            print("믹서가 초기화되지 않았습니다.")
            return
        try:
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            chord = np.zeros_like(t)
            for freq in frequencies:
                chord += np.sin(2 * np.pi * freq * t)
            chord = (chord * 32767 / len(frequencies)).astype(np.int16)
            sound = pygame.sndarray.make_sound(chord)
            sound.play()
            pygame.time.wait(int(duration * 1000))
        except Exception as e:
            print(f"화음 재생 중 오류 발생: {e}")

    def generate_correct_answer(self, key, chord_type):
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

    def generate_inversions(self, chord_notes):
        inversions = []
        
        # 상승
        for i in range(len(chord_notes)):
            inversion = chord_notes[i:] + [self.raise_octave(note) for note in chord_notes[:i]]
            inversions.append(inversion)
        
        # 상승 리스트를 평탄화
        ascending = [note for inversion in inversions for note in inversion]
        
        # 하강 (평탄화된 상승의 역순)
        descending = ascending[::-1]
        
        # 상승과 하강을 합침
        return ascending + descending

    def raise_octave(self, note):
        note_name, octave = note[:-1], int(note[-1])
        return f"{note_name}{octave + 1}"

    def lower_octave(self, note):
        note_name, octave = note[:-1], int(note[-1])
        return f"{note_name}{octave - 1}"

    def note_to_freq(self, note):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_name = note[:-1]
        octave = int(note[-1])
        base_freq = 261.6256  # C4의 주파수
        note_index = notes.index(note_name)
        c_index = notes.index('C')
        half_steps = note_index - c_index + (octave - 4) * 12
        freq = base_freq * (2 ** (half_steps / 12))
        return freq

def main():
    try:
        root = tk.Tk()
        app = HarmonyApp(root)
        root.mainloop()
    except Exception as e:
        print(f"애플리케이션 실 중 오류 발생: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()