# 🎵 Macan Audio Player

Macan Audio Player is a modern PyQt5-based audio player with support for various popular formats, powered by FFmpeg.
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

---

## 📸 Screenshot
<img width="850" height="674" alt="Screenshot 2025-09-17 162033" src="https://github.com/user-attachments/assets/81455c06-e56c-414a-b0ca-05bfb7725476" />


---

## 📝 Changelog v5.5.0
- Fixed minor bugs:
* when resuming playback after pausing
* showing duration in file properties that was previously N/A or unknown
- Added a Tag Editor feature for editing song information and album art

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
