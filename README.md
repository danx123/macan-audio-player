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
<img width="849" height="673" alt="Screenshot 2025-10-29 220711" src="https://github.com/user-attachments/assets/6fc152f3-c138-4e62-8796-7ccedf710c02" />
<img width="1080" height="1832" alt="macan-audio-player-v7" src="https://github.com/user-attachments/assets/9b4447ea-5e7c-434b-9234-9e8b767dd451" />


---

## 📝 Changelog v7.0.0
This is a quality-of-life update focused on enhancing playlist management, user interaction, and visual feedback.

### ✨ New Features

* **Playlist Context Menu: Remove Selected Track**
    * Users can now right-click a track in the playlist and select **"Remove Selected"** to delete it from the current session.
    * This action intelligently handles various playback scenarios:
        * If the currently playing track is removed, the player will stop and advance to the next track.
        * If the playlist becomes empty, the player UI is reset to its default state.
        * If a track *before* the currently playing track is removed, the playback index is automatically adjusted.

### 🎨 Enhancements

* **Upgraded Notification System:**
    * **Album Art Display:** Notifications (bubbles) now display the track's **album art** alongside the title and artist, providing richer visual feedback.
    * **Layout Consistency:** Corrected a layout calculation issue where notifications could have inconsistent sizing or screen placement, especially with long track titles. Notifications are now constrained to a maximum width and positioned reliably on the screen.

### 🔧 Refactors

* Introduced the `remove_selected_track` method to modularize the logic for track removal from the playlist.
* Refactored `NotificationWidget` to accept and process `artwork_data`, and switched its internal layout to `QHBoxLayout` to support the album art.
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
