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

## 📝 Changelog v7.5.0
🚀 New Features
Add File(s) Functionality
A new "Add File(s)" button and corresponding icon (add-file) have been added to the main control panel.
This allows users to select and add one or more individual audio files (e.g., .mp3, .flac) via a file dialog, supplementing the existing "Add Folder" capability.
Windows File Association
A "Register format" option has been added to the main options menu.
This feature allows users on Windows to associate supported audio formats (.mp3, .m4a, .ogg, .flac, .wav) with the Macan Audio Player.
The system now includes helper functions (is_admin, run_as_admin, perform_windows_registration) to check for administrator privileges, request UAC elevation, and safely modify the Windows Registry.
Code & Refactoring
Custom PlaylistWidget Class
The standard QListWidget for the playlist has been refactored into a new custom class, PlaylistWidget.
This change encapsulates the playlist's setup logic (e.g., drag/drop modes) and prepares the codebase for more advanced, playlist-specific features in the future.
Preparatory Code
Added a (currently unused) handle_playlist_drop method, indicating future work on enhancing drag-and-drop functionality directly onto the playlist widget.


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
