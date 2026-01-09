# 🎵 Macan Audio Player

Macan Audio Player is a modern PySide6-based audio player with support for various popular formats, powered by FFmpeg.
It features smooth lyrics sync (.lrc) with auto-follow, as well as manual lock for uninterrupted scrolling.

---

## ✨ Key Features
- Supports various popular audio formats (MP3, WAV, OGG, FLAC, AAC, etc.).
- Auto-Sync Lyrics (.lrc)
- Auto-follow lyrics to the song.
- Manual scroll lock → auto-follow stops when the user swipes.
- Toggle "Auto Follow Lyrics" via the menu.
- Dark & ​​Light themes with modern accents.
- Basic controls: Play, Pause, Seek (via slider).
- Simple, lightweight, and clean UI.
- Dynamic Aura
- Tag editor
- Online Radio
- Audio Normalization
- Advanced Tag Editor

---

## 📸 Screenshot
<img width="850" height="687" alt="Cuplikan layar 2026-01-09 195513" src="https://github.com/user-attachments/assets/84fd564f-3567-463f-b0f9-ec8b30f846f2" />



---

## 📝 Changelog v9.5.0
🚀 New Feature: Pro-Physics Visualizer

Physics-Based Animation: Implemented gravity and momentum systems. Visualizer bars now have "Attack" (jumping rapidly when a tone is played) and "Decay" (falling slowly following simulated gravity) effects.
Multi-Mode Display: Added three visualization modes that can be switched in real-time by left-clicking on the visualizer area:
1. Spectrum Bars: Classic bar display with curved corners.
2. Smooth Waveform: A Bezier curve-based visualization that flows like water (organic).
3. Mirrored Center: A symmetrical display that reflects from a center point for a modern aesthetic.

EQ Adaptive Sensitivity: The visualizer is now linked to the Equalizer settings. Increasing the Bass (60Hz) will automatically make the left area of ​​the visualizer more responsive.

🛠️ Fixes & Optimizations

- Zero CPU Overhead: Uses a sine wave and noise simulation technique that is much lighter than conventional FFT (Fast Fourier Transform) processing.
- Auto-Sleep Engine: The animation system will automatically shut down (*idle*) once the music stops and all bars have reached the bottom to conserve battery power.
- Smooth Rendering: Antialiasing support on every frame to ensure visualizer lines don't break or pixelate.
---

## 📦 Installation
1. Make sure **Python 3.10+** is installed.
2. Install dependencies:
```bash
pip install PyQt6
3. Make sure FFmpeg is installed and accessible via PATH.

---

📂 Note
The source code shared is the base project.
The full binary version (with the latest and stable features) is available in the Releases section.

---

📖 License
This project is licensed under the MIT license — free to use, modify, and distribute with proper credit.
