# Nama file: macan_audio_player_revised.py
# Deskripsi: Versi revisi dengan desain UI/UX yang lebih modern, rapi, dan ikon yang lebih estetik.
# Jalankan dengan perintah: python macan_audio_player_revised.py
#
# Pastikan pustaka yang dibutuhkan sudah terinstal:
# pip install PyQt6 PyQt6-QtMultimedia mutagen
#
# Perubahan dari versi sebelumnya:
# 1. [UI/UX] Desain ulang total antarmuka agar lebih bersih, modern, dan tidak terlalu besar.
#    - Layout diatur ulang untuk alur visual yang lebih baik.
#    - Ukuran jendela dan widget disesuaikan agar lebih kompak.
# 2. [AESTHETICS] Ikon SVG diganti dengan set ikon yang lebih modern dan konsisten.
# 3. [STYLE] Stylesheet (QSS) diperbarui untuk mencerminkan desain baru, dengan warna dan spasi yang lebih baik.
# 4. [REFACTOR] Kode pembuatan UI dipecah menjadi beberapa fungsi untuk keterbacaan yang lebih baik.
# 5. [FIX] Mempertahankan perbaikan dari versi sebelumnya (Base64 error dan seekbar yang bisa diklik).

import sys
import os
import random
import base64
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QStatusBar, QDialog, QGridLayout, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize, QSettings
from PyQt6.QtGui import QIcon, QPainter, QColor, QAction, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Import pustaka untuk metadata
try:
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.id3 import APIC
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# --- [AESTHETICS] DATA SVG IKON BARU YANG LEBIH MODERN (Base64 Encoded) ---
SVG_ICONS = {
    "play": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDMgMTkgMTIgNSAyMSA1IDMiPjwvcG9seWdvbj48L3N2Zz4=",
    "pause": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iNiIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iMTYiPjwvcmVjdD48cmVjdCB4PSIxNCIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iMTYiPjwvcmVjdD48L3N2Zz4=",
    "next": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iNSA0IDE1IDEyIDUgMjAgNSA0Ij48L3BvbHlnb24+PGxpbmUgeDE9IjE5IiB5MT0iNSIgeDI9IjE5IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "previous": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTkgNCA5IDEyIDE5IDIwIDE5IDQiPjwvcG9seWdvbj48bGluZSB4MT0iNSIgeTE9IjUiIHgyPSI1IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "volume-high": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PHBhdGggZD0iTTE1LjU0IDguNDZhNSA1IDAgMCAxIDAgNy4wNyI+PC9wYXRoPjwvc3ZnPg==",
    "volume-muted": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PGxpbmUgeDE9IjIzIiB5MT0iOSIgeDI9IjE3IiB5Mj0iMTUiPjwvbGluZT48bGluZSB4MT0iMTciIHkxPSI5IiB4Mj0iMjMiIHkyPSIxNSI+PC9saW5lPjwvc3ZnPg==",
    "add-folder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMiAxOWEyIDIgMCAwIDEtMiAySDRhMiAyIDAgMCAxLTItMlY1YTIgMiAwIDAgMSAyLTJoNWwyIDNoOWEyIDIgMCAwIDEgMiAyeiI+PC9wYXRoPjxsaW5lIHgxPSIxMiIgeTE9IjExIiB4Mj0iMTIiIHkyPSIxNyI+PC9saW5lPjxsaW5lIHgxPSI5IiB5MT0iMTQiIHgyPSIxNSIgeTI9IjE0Ij48L2xpbmU+PC9zdmc+",
    "clear-playlist": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5bGluZSBwb2ludHM9IjMgNiA1IDYgMjEgNiI+PC9wb2x5bGluZT48cGF0aCBkPSJNMTkgNnYxNGEyIDIgMCAwIDEtMiAySDdhMiAyIDAgMCAxLTItMlY2bTMgMFY0YTIgMiAwIDAgMSAyLTJoNGEyIDIgMCAwIDEgMiAydjIiPjwvcGF0aD48L3N2Zz4=",
    "album-placeholder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM0QTQ5NDQiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIj48L2NpcmNsZT48L3N2Zz4="
}

def get_icon_from_svg(svg_data_base64, color="#E0E0E0"):
    """Membuat QIcon dari data SVG, memungkinkan penggantian warna."""
    try:
        svg_data_str = base64.b64decode(svg_data_base64).decode('utf-8')
        # Ganti 'currentColor' dengan warna spesifik untuk rendering yang konsisten
        svg_data_colored = svg_data_str.replace('currentColor', color)
        
        renderer = QSvgRenderer(svg_data_colored.encode('utf-8'))
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon() # Fallback

# Kelas ClickableSlider tetap sama
class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width()
            self.setValue(int(value))
            self.sliderMoved.emit(int(value))
        super().mousePressEvent(event)

# Kelas VisualizerWidget tetap sama
class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40) # [UI/UX] Dibuat lebih pendek
        self.bars = [0] * 40
        self.equalizer_settings = {'bass': 0, 'mid': 0, 'treble': 0}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)

    def start(self): self.timer.start(50)
    def stop(self):
        self.timer.stop()
        self.bars = [0] * 40
        self.update()

    def set_equalizer_settings(self, settings): self.equalizer_settings = settings

    def update_bars(self):
        num_bars = len(self.bars)
        for i in range(num_bars):
            base_height = random.randint(1, self.height() // 2)
            if i < num_bars / 3: eq_mod = self.equalizer_settings['bass'] / 100.0
            elif i < num_bars * 2 / 3: eq_mod = self.equalizer_settings['mid'] / 100.0
            else: eq_mod = self.equalizer_settings['treble'] / 100.0
            self.bars[i] = int(base_height * (1 + eq_mod))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        bar_width = self.width() / len(self.bars)
        for i, bar_height in enumerate(self.bars):
            color = QColor("#0d6efd") # Biru yang lebih vibrant
            color.setAlphaF(0.8)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            x = i * bar_width
            y = self.height() // 2 - bar_height // 2
            height = max(1, bar_height)
            painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(height), 2, 2)

# Kelas EqualizerDialog tetap sama
class EqualizerDialog(QDialog):
    equalizer_updated = pyqtSignal(dict)
    def __init__(self, parent=None, initial_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Equalizer")
        self.setFixedSize(300, 200)
        self.equalizer_settings = initial_settings or {'bass': 0, 'mid': 0, 'treble': 0}
        main_layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        self.bass_slider = self._create_slider('bass', self.equalizer_settings['bass'], grid_layout, 0)
        self.mid_slider = self._create_slider('mid', self.equalizer_settings['mid'], grid_layout, 1)
        self.treble_slider = self._create_slider('treble', self.equalizer_settings['treble'], grid_layout, 2)
        main_layout.addLayout(grid_layout)
        self.bass_slider.valueChanged.connect(self.update_settings)
        self.mid_slider.valueChanged.connect(self.update_settings)
        self.treble_slider.valueChanged.connect(self.update_settings)
        self.setStyleSheet(parent.styleSheet())

    def _create_slider(self, name, value, layout, column):
        label = QLabel(name.capitalize())
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setRange(-100, 100)
        slider.setValue(value)
        slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        slider.setTickInterval(50)
        layout.addWidget(slider, 0, column, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 1, column, Qt.AlignmentFlag.AlignCenter)
        return slider

    def update_settings(self):
        self.equalizer_settings['bass'] = self.bass_slider.value()
        self.equalizer_settings['mid'] = self.mid_slider.value()
        self.equalizer_settings['treble'] = self.treble_slider.value()
        self.equalizer_updated.emit(self.equalizer_settings)


# --- Kelas Utama Aplikasi Pemutar Audio ---
class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Audio Player 🎵")
        # [UI/UX] Ukuran window awal dibuat lebih kompak
        self.setGeometry(100, 100, 480, 720) 
        self.setMinimumSize(400, 600)
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self.settings = QSettings("MacanCorp", "MacanAudioPlayerRevised")
        self.playlist = []
        self.current_index = -1
        self.is_muted = False
        self.last_volume = 100
        self.equalizer_settings = {'bass': 0, 'mid': 0, 'treble': 0}
        
        self.setStatusBar(QStatusBar())
        self.setup_ui()
        self.setup_connections()
        self.apply_stylesheet()
        self.load_settings()

    # [REFACTOR] Fungsi setup_ui dipecah menjadi beberapa bagian
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.create_menu_bar()
        
        # [UI/UX] Layout baru yang lebih terstruktur
        main_layout.addLayout(self.create_info_panel())
        main_layout.addLayout(self.create_seekbar_panel())
        main_layout.addLayout(self.create_playback_controls())
        main_layout.addLayout(self.create_bottom_panel())
        
        self.playlist_widget = QListWidget()
        self.playlist_widget.setObjectName("playlistWidget")
        main_layout.addWidget(self.playlist_widget, 1)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Opsi")
        equalizer_action = QAction("Equalizer", self)
        equalizer_action.triggered.connect(self.show_equalizer_dialog)
        options_menu.addAction(equalizer_action)

    def create_info_panel(self):
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        self.album_art_label = QLabel()
        self.album_art_label.setObjectName("albumArt")
        # [UI/UX] Ukuran album art disesuaikan
        self.album_art_label.setFixedSize(180, 180) 
        self.album_art_label.setScaledContents(True)
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        renderer = QSvgRenderer(base64.b64decode(SVG_ICONS["album-placeholder"]))
        self.default_album_art = QPixmap(self.album_art_label.size())
        self.default_album_art.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.default_album_art)
        renderer.render(painter)
        painter.end()
        self.album_art_label.setPixmap(self.default_album_art.scaled(
            self.album_art_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        
        self.track_title_label = QLabel("Tidak Ada Lagu")
        self.track_title_label.setObjectName("trackTitle")
        self.track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_title_label.setWordWrap(True)
        
        self.artist_label = QLabel("Pilih lagu untuk diputar")
        self.artist_label.setObjectName("artistLabel")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.visualizer_widget = VisualizerWidget()
        
        # [UI/UX] Menata ulang widget informasi
        top_wrapper_layout = QHBoxLayout()
        top_wrapper_layout.addStretch()
        top_wrapper_layout.addWidget(self.album_art_label)
        top_wrapper_layout.addStretch()

        info_layout.addLayout(top_wrapper_layout)
        info_layout.addWidget(self.track_title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.visualizer_widget)
        
        return info_layout

    def create_seekbar_panel(self):
        seekbar_layout = QVBoxLayout()
        seekbar_layout.setSpacing(5)
        
        self.seekbar = ClickableSlider(Qt.Orientation.Horizontal)
        self.seekbar.setRange(0, 0)
        
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        
        seekbar_layout.addWidget(self.seekbar)
        seekbar_layout.addLayout(time_layout)
        return seekbar_layout

    def create_playback_controls(self):
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20)
        self.prev_button = self._create_button("previous", "Lagu Sebelumnya", "secondaryButton")
        self.play_button = self._create_button("play", "Putar", "mainButton", use_theme_color=True)
        self.next_button = self._create_button("next", "Lagu Berikutnya", "secondaryButton")

        control_layout.addStretch()
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addStretch()
        return control_layout

    def create_bottom_panel(self):
        bottom_layout = QHBoxLayout()
        
        self.volume_button = self._create_button("volume-high", "Mute/Unmute", "iconButton")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setFixedWidth(120)
        
        bottom_layout.addWidget(self.volume_button)
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addStretch()
        
        self.add_folder_button = self._create_button("add-folder", "Tambah Folder", "iconButton")
        self.clear_playlist_button = self._create_button("clear-playlist", "Bersihkan Playlist", "iconButton")
        bottom_layout.addWidget(self.add_folder_button)
        bottom_layout.addWidget(self.clear_playlist_button)
        return bottom_layout

    def _create_button(self, icon_name, tooltip, object_name=None, use_theme_color=False):
        button = QPushButton()
        # Ikon pada tombol utama diwarnai putih agar kontras dengan background biru
        icon_color = "#FFFFFF" if use_theme_color else "#E0E0E0"
        button.setIcon(get_icon_from_svg(SVG_ICONS[icon_name], color=icon_color))
        button.setToolTip(tooltip)
        if object_name:
            button.setObjectName(object_name)
        return button

    # --- Sisa fungsi (setup_connections, load_settings, dll.) sebagian besar tetap sama ---
    # Tidak ada perubahan logika, hanya penyesuaian UI.

    def setup_connections(self):
        self.play_button.clicked.connect(self.play_pause_music)
        self.next_button.clicked.connect(self.next_track)
        self.prev_button.clicked.connect(self.prev_track)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.clear_playlist_button.clicked.connect(self.clear_playlist)
        self.playlist_widget.doubleClicked.connect(self.play_selected_track)
        
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        
        self.seekbar.sliderMoved.connect(self.set_position)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_button.clicked.connect(self.toggle_mute)
        
    def load_settings(self):
        loaded_playlist = self.settings.value("playlist", [], type=list)
        if loaded_playlist:
            valid_playlist = [path for path in loaded_playlist if os.path.exists(path)]
            self.playlist = valid_playlist
            for track_path in self.playlist:
                self.playlist_widget.addItem(os.path.basename(track_path))
            if self.playlist:
                self.current_index = 0
                self.playlist_widget.setCurrentRow(0)
                self.update_track_info(self.playlist[0])
        
        eq_settings = self.settings.value("equalizer", self.equalizer_settings, type=dict)
        self.equalizer_settings = eq_settings
        self.visualizer_widget.set_equalizer_settings(self.equalizer_settings)
        
        volume = self.settings.value("volume", 100, type=int)
        self.last_volume = volume
        self.volume_slider.setValue(volume)
        self.audio_output.setVolume(volume / 100.0)

    def closeEvent(self, event):
        self.settings.setValue("playlist", self.playlist)
        self.settings.setValue("equalizer", self.equalizer_settings)
        self.settings.setValue("volume", self.volume_slider.value())
        self.player.stop()
        event.accept()

    def play_pause_music(self):
        if not self.playlist:
            QMessageBox.information(self, "Informasi", "Playlist kosong. Silakan tambahkan lagu.")
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"], color="#FFFFFF"))
            self.visualizer_widget.stop()
        else:
            if self.current_index == -1: self.current_index = 0
            self.play_current_track()

    def next_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current_track()

    def prev_track(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
        self.play_current_track()
        
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Musik")
        if folder_path:
            supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
            new_tracks_count = 0
            for filename in sorted(os.listdir(folder_path)):
                if any(filename.lower().endswith(ext) for ext in supported_formats):
                    full_path = os.path.join(folder_path, filename)
                    if full_path not in self.playlist:
                        self.playlist.append(full_path)
                        title = self.get_track_metadata(full_path).get('title', filename)
                        self.playlist_widget.addItem(title)
                        new_tracks_count += 1
            if new_tracks_count > 0:
                self.statusBar().showMessage(f"Ditambahkan {new_tracks_count} lagu baru.")
                if self.current_index == -1:
                    self.current_index = 0
                    self.playlist_widget.setCurrentRow(0)
                    self.update_track_info(self.playlist[0])
            else:
                self.statusBar().showMessage("Tidak ada lagu baru yang ditemukan.")
    
    def clear_playlist(self):
        self.player.stop()
        self.playlist.clear()
        self.playlist_widget.clear()
        self.current_index = -1
        self.reset_ui_info()
        self.visualizer_widget.stop()
        self.statusBar().showMessage("Playlist berhasil dibersihkan.")

    def play_selected_track(self):
        self.current_index = self.playlist_widget.currentRow()
        self.play_current_track()

    def play_current_track(self):
        if 0 <= self.current_index < len(self.playlist):
            track_path = self.playlist[self.current_index]
            self.player.setSource(QUrl.fromLocalFile(track_path))
            self.player.play()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"], color="#FFFFFF"))
            self.update_track_info(track_path)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start()
            
    def update_track_info(self, track_path):
        metadata = self.get_track_metadata(track_path)
        self.track_title_label.setText(metadata.get('title', 'Unknown Title'))
        self.artist_label.setText(metadata.get('artist', 'Unknown Artist'))
        if metadata.get('artwork'):
            pixmap = QPixmap()
            pixmap.loadFromData(metadata['artwork'])
            self.album_art_label.setPixmap(pixmap.scaled(
                self.album_art_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.album_art_label.setPixmap(self.default_album_art)

    def get_track_metadata(self, path):
        metadata = {'title': os.path.basename(path), 'artist': 'Unknown Artist', 'artwork': None}
        if not MUTAGEN_AVAILABLE: return metadata

        try:
            if path.lower().endswith('.mp3'):
                audio = MP3(path)
                metadata['title'] = str(audio.get('TIT2', [metadata['title']])[0])
                metadata['artist'] = str(audio.get('TPE1', [metadata['artist']])[0])
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        metadata['artwork'] = tag.data; break
            elif path.lower().endswith('.flac'):
                audio = FLAC(path)
                metadata['title'] = audio.get('title', [metadata['title']])[0]
                metadata['artist'] = audio.get('artist', [metadata['artist']])[0]
                if audio.pictures: metadata['artwork'] = audio.pictures[0].data
            elif path.lower().endswith('.m4a'):
                audio = MP4(path)
                metadata['title'] = audio.get('\xa9nam', [metadata['title']])[0]
                metadata['artist'] = audio.get('\xa9ART', [metadata['artist']])[0]
                if '\xa9covr' in audio and audio['\xa9covr']: metadata['artwork'] = audio['\xa9covr'][0]
        except Exception:
            pass
        return metadata

    def reset_ui_info(self):
        self.track_title_label.setText("Tidak Ada Lagu")
        self.artist_label.setText("Playlist kosong")
        self.album_art_label.setPixmap(self.default_album_art)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self.seekbar.setValue(0)
        self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"], color="#FFFFFF"))

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_position(self, position):
        if not self.seekbar.isSliderDown(): self.seekbar.setValue(position)
        self.current_time_label.setText(self.format_time(position))

    def update_duration(self, duration):
        self.seekbar.setRange(0, duration)
        self.total_time_label.setText(self.format_time(duration))

    def set_position(self, position):
        self.player.setPosition(position)
        
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
        if value > 0:
            if self.is_muted: self.is_muted = False
            self.last_volume = value
            self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS["volume-high"]))
        else:
            self.is_muted = True
            self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS["volume-muted"]))

    def toggle_mute(self):
        if self.is_muted:
            self.volume_slider.setValue(self.last_volume)
        else:
            self.last_volume = self.volume_slider.value()
            if self.last_volume == 0: self.last_volume = 75
            self.volume_slider.setValue(0)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia: self.next_track()

    def show_equalizer_dialog(self):
        eq_dialog = EqualizerDialog(self, self.equalizer_settings)
        eq_dialog.equalizer_updated.connect(self.update_equalizer_settings)
        eq_dialog.exec()

    def update_equalizer_settings(self, settings):
        self.equalizer_settings = settings
        self.visualizer_widget.set_equalizer_settings(settings)
        self.statusBar().showMessage("Pengaturan Equalizer diperbarui!")

    def apply_stylesheet(self):
        # [STYLE] QSS disesuaikan dengan desain baru
        qss = """
            QMainWindow, QDialog { background-color: #181818; }
            QWidget { color: #E0E0E0; font-family: Segoe UI, sans-serif; font-size: 14px; }
            QMenuBar { background-color: #1F1F1F; }
            QMenuBar::item:selected { background-color: #0d6efd; }
            QMenu { background-color: #282828; border: 1px solid #444; }
            QMenu::item:selected { background-color: #0d6efd; }
            QStatusBar { color: #A0A0A0; background-color: #1F1F1F; }
            
            #albumArt { border: none; border-radius: 12px; }
            #trackTitle { font-size: 22px; font-weight: bold; }
            #artistLabel { font-size: 16px; color: #B0B0B0; }
            
            #playlistWidget {
                background-color: #121212; border: 1px solid #282828;
                border-radius: 8px; padding: 5px;
            }
            #playlistWidget::item { padding: 10px; border-radius: 5px; }
            #playlistWidget::item:selected { background-color: #0d6efd; color: #FFFFFF; }
            #playlistWidget::item:hover:!selected { background-color: #2A2A2A; }

            QSlider::groove:horizontal {
                border: 1px solid #333; height: 8px; background: #282828;
                margin: 2px 0; border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #E0E0E0; border: 1px solid #E0E0E0;
                width: 16px; margin: -4px 0; border-radius: 8px;
            }
            QSlider::handle:horizontal:hover { background: #0d6efd; border: 1px solid #0d6efd; }
            QSlider::sub-page:horizontal { background: #0d6efd; border-radius: 4px; }

            QPushButton { border: none; background-color: transparent; }
            #mainButton {
                background-color: #0d6efd; color: #FFFFFF;
                border-radius: 32px;
                min-width: 64px; min-height: 64px;
                padding: 8px;
            }
            #mainButton:hover { background-color: #0b5ed7; }
            #secondaryButton {
                background-color: transparent;
                border-radius: 25px;
                min-width: 50px; min-height: 50px;
            }
            #iconButton {
                border-radius: 20px;
                min-width: 40px; min-height: 40px;
            }
            #secondaryButton:hover, #iconButton:hover { background-color: #2A2A2A; }
            #mainButton:pressed, #secondaryButton:pressed, #iconButton:pressed { background-color: #444; }
            
            QLabel { background-color: transparent; }
        """
        self.setStyleSheet(qss)

if __name__ == '__main__':
    # Peringatan Mutagen tetap ada karena penting
    app = QApplication(sys.argv)
    if not MUTAGEN_AVAILABLE:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("Pustaka 'mutagen' tidak ditemukan.")
        msg_box.setInformativeText("Fitur metadata (judul, artis, sampul) tidak akan berfungsi.\nInstall dengan: pip install mutagen")
        msg_box.setWindowTitle("Peringatan")
        msg_box.exec()

    player = AudioPlayer()
    player.show()
    sys.exit(app.exec())