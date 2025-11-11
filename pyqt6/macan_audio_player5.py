# Nama file: macan_audio_player_revised.py
# Deskripsi: Pemutar audio yang telah diperbaiki, didesain ulang, dan dioptimalkan.
# Jalankan dengan perintah: python macan_audio_player_revised.py
#
# Pastikan pustaka yang dibutuhkan sudah terinstal:
# pip install PyQt6 PyQt6-QtMultimedia mutagen
#
# Perubahan dari versi sebelumnya:
# 1. [FIX] Kesalahan penanganan ikon SVG diperbaiki dengan memuat file .svg eksternal.
# 2. [REDESIGN] UI/Layout dirombak total untuk tampilan modern, profesional, dan estetik.
#    - Menambahkan area sampul album (album art).
#    - Menata ulang kontrol pemutaran, volume, dan playlist.
#    - Menambahkan label waktu/durasi pada seekbar.
#    - Stylesheet (QSS) premium baru untuk semua elemen.
# 3. [OPTIMIZE] Menambahkan fungsionalitas ekstraksi metadata (judul, artis, sampul).
#    - Menggunakan pustaka 'mutagen' untuk membaca metadata file audio.
#    - Kode dipecah menjadi fungsi-fungsi yang lebih terstruktur dan mudah dibaca.
#    - Menyimpan dan memuat status volume.

import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QStatusBar, QDialog, QGridLayout, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize, QSettings
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QAction, QPixmap
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

# --- Kelas Widget Visualizer (Tetap sama, hanya integrasi yang diubah) ---
class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.bars = [0] * 50
        self.equalizer_settings = {'bass': 0, 'mid': 0, 'treble': 0}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)

    def start(self): self.timer.start(50)
    def stop(self):
        self.timer.stop()
        self.bars = [0] * 50
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
            color = QColor("#007BFF")
            color.setAlphaF(0.7)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            x = i * bar_width
            y = self.height() // 2 - bar_height // 2
            height = max(1, bar_height)
            painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(height), 2, 2)


# --- Kelas Dialog Equalizer (Minor Style Update) ---
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
        self.setStyleSheet(parent.styleSheet()) # Inherit stylesheet

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
        self.setGeometry(100, 100, 550, 750)
        self.setMinimumSize(450, 450)
        
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

    def setup_ui(self):
        """Mempersiapkan semua widget dan layout utama (struktur baru)."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Membuat menu
        self.create_menu_bar()

        # Panel Informasi (Cover, Judul, Artis, Visualizer)
        main_layout.addLayout(self.create_info_panel())

        # Panel Seekbar (Waktu, Slider, Durasi)
        main_layout.addLayout(self.create_seekbar_panel())

        # Panel Kontrol (Prev, Play/Pause, Next)
        main_layout.addLayout(self.create_playback_controls())
        
        # Panel Bawah (Volume dan Kontrol Playlist)
        main_layout.addLayout(self.create_bottom_panel())

        # Widget Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.setObjectName("playlistWidget")
        main_layout.addWidget(self.playlist_widget, 1) # Stretch factor

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Opsi")
        equalizer_action = QAction("Equalizer", self)
        equalizer_action.triggered.connect(self.show_equalizer_dialog)
        options_menu.addAction(equalizer_action)

    def create_info_panel(self):
        """Membuat panel atas yang berisi sampul, info lagu, dan visualizer."""
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        # Sampul Album
        self.album_art_label = QLabel()
        self.album_art_label.setObjectName("albumArt")
        self.album_art_label.setFixedSize(180, 180)
        self.album_art_label.setScaledContents(True)
        self.default_album_art = QPixmap("icons/album-placeholder.svg")
        self.album_art_label.setPixmap(self.default_album_art)
        info_layout.addWidget(self.album_art_label)

        # Kolom Kanan (Info Teks dan Visualizer)
        right_column_layout = QVBoxLayout()
        self.track_title_label = QLabel("Tidak Ada Lagu")
        self.track_title_label.setObjectName("trackTitle")
        self.track_title_label.setWordWrap(True)
        
        self.artist_label = QLabel("Pilih lagu untuk diputar")
        self.artist_label.setObjectName("artistLabel")

        self.visualizer_widget = VisualizerWidget()
        
        right_column_layout.addWidget(self.track_title_label)
        right_column_layout.addWidget(self.artist_label)
        right_column_layout.addStretch()
        right_column_layout.addWidget(self.visualizer_widget)
        
        info_layout.addLayout(right_column_layout, 1)
        return info_layout

    def create_seekbar_panel(self):
        """Membuat panel seekbar dengan label waktu."""
        seekbar_layout = QVBoxLayout()
        seekbar_layout.setSpacing(5)
        
        self.seekbar = QSlider(Qt.Orientation.Horizontal)
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
        """Membuat kontrol pemutaran utama."""
        control_layout = QHBoxLayout()
        control_layout.setSpacing(20)
        self.prev_button = self._create_button("previous", "Lagu Sebelumnya", "secondaryButton")
        self.play_button = self._create_button("play", "Putar", "mainButton")
        self.play_button.setIconSize(QSize(40, 40))
        self.next_button = self._create_button("next", "Lagu Berikutnya", "secondaryButton")

        control_layout.addStretch()
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addStretch()
        return control_layout

    def create_bottom_panel(self):
        """Membuat panel bawah untuk volume dan aksi playlist."""
        bottom_layout = QHBoxLayout()
        
        # Kontrol Volume
        self.volume_button = self._create_button("volume-high", "Mute/Unmute", "iconButton")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setFixedWidth(120)
        
        bottom_layout.addWidget(self.volume_button)
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addStretch()
        
        # Kontrol Playlist
        self.add_folder_button = self._create_button("add-folder", "Tambah Folder", "iconButton")
        self.clear_playlist_button = self._create_button("clear-playlist", "Bersihkan Playlist", "iconButton")
        bottom_layout.addWidget(self.add_folder_button)
        bottom_layout.addWidget(self.clear_playlist_button)
        return bottom_layout

    def _create_button(self, icon_name, tooltip, object_name=None):
        """Helper untuk membuat QPushButton dengan ikon dari file SVG."""
        button = QPushButton()
        button.setIcon(QIcon(f"icons/{icon_name}.svg"))
        button.setToolTip(tooltip)
        if object_name:
            button.setObjectName(object_name)
        return button

    def setup_connections(self):
        """Menghubungkan sinyal-sinyal dari widget ke slot/fungsi."""
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
        
    # --- Fungsi Logika Inti (Sebagian besar sama, dengan tambahan metadata) ---
    def load_settings(self):
        """Memuat pengaturan (playlist, volume, equalizer) saat aplikasi dimulai."""
        # Muat playlist
        loaded_playlist = self.settings.value("playlist", [], type=list)
        if loaded_playlist:
            valid_playlist = [path for path in loaded_playlist if os.path.exists(path)]
            self.playlist = valid_playlist
            for track_path in self.playlist:
                self.playlist_widget.addItem(os.path.basename(track_path))
            if self.playlist:
                self.current_index = 0
                self.playlist_widget.setCurrentRow(0)
                self.update_track_info(self.playlist[0]) # Tampilkan info lagu pertama
        
        # Muat equalizer
        eq_settings = self.settings.value("equalizer", self.equalizer_settings, type=dict)
        self.equalizer_settings = eq_settings
        self.visualizer_widget.set_equalizer_settings(self.equalizer_settings)
        
        # Muat volume
        volume = self.settings.value("volume", 100, type=int)
        self.last_volume = volume
        self.volume_slider.setValue(volume)
        self.audio_output.setVolume(volume / 100.0)

    def closeEvent(self, event):
        """Menyimpan pengaturan saat aplikasi ditutup."""
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
            self.play_button.setIcon(QIcon("icons/play.svg"))
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
                if self.current_index == -1: # Jika ini lagu pertama yang ditambah
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
            self.play_button.setIcon(QIcon("icons/pause.svg"))
            self.update_track_info(track_path)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start()
            
    def update_track_info(self, track_path):
        """Memperbarui UI dengan metadata lagu."""
        metadata = self.get_track_metadata(track_path)
        self.track_title_label.setText(metadata.get('title', 'Unknown Title'))
        self.artist_label.setText(metadata.get('artist', 'Unknown Artist'))
        if metadata.get('artwork'):
            pixmap = QPixmap()
            pixmap.loadFromData(metadata['artwork'])
            self.album_art_label.setPixmap(pixmap)
        else:
            self.album_art_label.setPixmap(self.default_album_art)

    def get_track_metadata(self, path):
        """Mengekstrak metadata dari file audio menggunakan Mutagen."""
        metadata = {'title': os.path.basename(path), 'artist': 'Unknown Artist', 'artwork': None}
        if not MUTAGEN_AVAILABLE: return metadata

        try:
            if path.lower().endswith('.mp3'):
                audio = MP3(path)
                metadata['title'] = audio.get('TIT2', [metadata['title']])[0]
                metadata['artist'] = audio.get('TPE1', [metadata['artist']])[0]
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        metadata['artwork'] = tag.data
                        break
            elif path.lower().endswith('.flac'):
                audio = FLAC(path)
                metadata['title'] = audio.get('title', [metadata['title']])[0]
                metadata['artist'] = audio.get('artist', [metadata['artist']])[0]
                if audio.pictures: metadata['artwork'] = audio.pictures[0].data
            elif path.lower().endswith('.m4a'):
                audio = MP4(path)
                metadata['title'] = audio.get('\xa9nam', [metadata['title']])[0]
                metadata['artist'] = audio.get('\xa9ART', [metadata['artist']])[0]
                if '\xa9covr' in audio and audio['\xa9covr']:
                    metadata['artwork'] = audio['\xa9covr'][0]
        except Exception:
            pass # Gagal membaca metadata, gunakan default
        return metadata

    def reset_ui_info(self):
        self.track_title_label.setText("Tidak Ada Lagu")
        self.artist_label.setText("Playlist kosong")
        self.album_art_label.setPixmap(self.default_album_art)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self.seekbar.setValue(0)
        self.play_button.setIcon(QIcon("icons/play.svg"))

    def format_time(self, ms):
        """Mengubah milidetik menjadi format MM:SS."""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_position(self, position):
        if not self.seekbar.isSliderDown():
            self.seekbar.setValue(position)
        self.current_time_label.setText(self.format_time(position))

    def update_duration(self, duration):
        self.seekbar.setRange(0, duration)
        self.total_time_label.setText(self.format_time(duration))

    def set_position(self, position):
        self.player.setPosition(position)
        
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
        if value > 0:
            self.is_muted = False
            self.last_volume = value
            self.volume_button.setIcon(QIcon("icons/volume-high.svg"))
        else:
            self.is_muted = True
            self.volume_button.setIcon(QIcon("icons/volume-muted.svg"))

    def toggle_mute(self):
        if self.is_muted: # Unmute
            self.volume_slider.setValue(self.last_volume)
        else: # Mute
            self.last_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
        self.is_muted = not self.is_muted
        
    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track()

    def show_equalizer_dialog(self):
        eq_dialog = EqualizerDialog(self, self.equalizer_settings)
        eq_dialog.equalizer_updated.connect(self.update_equalizer_settings)
        eq_dialog.exec()

    def update_equalizer_settings(self, settings):
        self.equalizer_settings = settings
        self.visualizer_widget.set_equalizer_settings(settings)
        self.statusBar().showMessage("Pengaturan Equalizer diperbarui!")

    def apply_stylesheet(self):
        """Menerapkan stylesheet (QSS) premium baru."""
        qss = """
            QMainWindow { background-color: #121212; }
            QWidget { color: #E0E0E0; font-family: Segoe UI, sans-serif; }
            QMenuBar { background-color: #1F1F1F; border-bottom: 1px solid #333; }
            QMenuBar::item { color: #E0E0E0; padding: 5px 15px; }
            QMenuBar::item:selected { background-color: #007BFF; }
            QMenu { background-color: #282828; border: 1px solid #444; }
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #007BFF; }
            QStatusBar { color: #A0A0A0; background-color: #1F1F1F; border-top: 1px solid #333; }
            
            #albumArt { border: 2px solid #282828; border-radius: 12px; }
            #trackTitle { font-size: 22px; font-weight: bold; }
            #artistLabel { font-size: 16px; color: #B0B0B0; }
            
            #playlistWidget {
                background-color: #181818;
                border: 1px solid #282828;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
            }
            #playlistWidget::item { padding: 8px; border-radius: 4px; }
            #playlistWidget::item:selected { background-color: #333; color: #007BFF; }
            #playlistWidget::item:hover { background-color: #2A2A2A; }

            QSlider::groove:horizontal {
                border: 1px solid #333;
                height: 6px;
                background: #282828;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #E0E0E0;
                border: 1px solid #E0E0E0;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover { background: #007BFF; border: 1px solid #007BFF; }
            QSlider::sub-page:horizontal { background: #007BFF; border-radius: 3px; }

            QPushButton { border: none; background-color: transparent; }
            #mainButton {
                background-color: #007BFF;
                border-radius: 35px;
                min-width: 70px; min-height: 70px;
                padding: 5px;
            }
            #mainButton:hover { background-color: #009CFF; }
            #secondaryButton, #iconButton {
                background-color: #282828;
                border-radius: 25px;
                min-width: 50px; min-height: 50px;
            }
            #secondaryButton:hover, #iconButton:hover { background-color: #383838; }
            #mainButton:pressed, #secondaryButton:pressed, #iconButton:pressed { background-color: #444; }
            
            QLabel { background-color: transparent; }
            QDialog { background-color: #181818; }
        """
        self.setStyleSheet(qss)

if __name__ == '__main__':
    if not os.path.exists("icons"):
        QMessageBox.critical(None, "Error", "Folder 'icons' tidak ditemukan. Pastikan folder dan file-file SVG sudah ada.")
        sys.exit(1)
    if not MUTAGEN_AVAILABLE:
        QMessageBox.warning(None, "Peringatan", "Pustaka 'mutagen' tidak ditemukan.\nFitur metadata (judul, artis, sampul) tidak akan berfungsi.\n\nInstall dengan: pip install mutagen")

    app = QApplication(sys.argv)
    player = AudioPlayer()
    player.show()
    sys.exit(app.exec())