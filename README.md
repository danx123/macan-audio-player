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
<img width="848" height="668" alt="Screenshot 2025-11-11 085102" src="https://github.com/user-attachments/assets/a3230efe-d5e0-4055-bfca-54b86ddc994f" />




---

## 📝 Changelog v7.8.0
Fixes & Enhancements
Playlist Insertion Logic: Fixed an issue where new tracks added via the "Add File(s)" button or drag-and-drop were always appended to the end of the list. New files are now inserted directly below the currently playing track for improved queue management.
Playlist Multi-Selection: Enabled extended selection (Shift + Ctrl) in the playlist widget, allowing users to select and manage multiple tracks simultaneously.


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
