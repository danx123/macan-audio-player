# Nama file: macan_audio_player_visualizer.py
# Jalankan dengan perintah: python macan_audio_player_visualizer.py
#
# Pastikan pustaka yang dibutuhkan sudah terinstal:
# pip install PyQt6
# pip install PyQt6-QtMultimedia
#
# Catatan: Visualizer ini adalah simulasi. Untuk visualizer real-time yang akurat,
# diperlukan pustaka tambahan untuk menganalisis data audio (misalnya: numpy, sounddevice).
# Implementasi di bawah ini menggunakan QTimer untuk memperbarui animasi.

import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QStatusBar
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# --- Kelas Widget Visualizer BARU ---
class VisualizerWidget(QWidget):
    """
    Widget kustom untuk menggambar visualizer audio yang disimulasikan.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.bars = [0] * 50 # Daftar untuk menyimpan tinggi bar
        
        # QTimer untuk memperbarui animasi
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        
    def start(self):
        """Memulai animasi visualizer."""
        self.timer.start(50) # Perbarui setiap 50 ms

    def stop(self):
        """Menghentikan animasi visualizer."""
        self.timer.stop()
        self.bars = [0] * 50
        self.update() # Paksa repaint untuk mereset visualizer

    def update_bars(self):
        """Memperbarui tinggi bar secara acak untuk simulasi."""
        for i in range(len(self.bars)):
            # Perbarui tinggi bar secara acak
            self.bars[i] = random.randint(1, self.height() // 2)
        self.update() # Paksa repaint widget

    def paintEvent(self, event):
        """Fungsi utama untuk menggambar visualizer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Mengisi latar belakang
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        # Konfigurasi pena dan kuas
        bar_width = self.width() // len(self.bars)
        bar_spacing = 2
        
        # Menggambar setiap bar
        for i, bar_height in enumerate(self.bars):
            # Menggambar setiap bar dengan warna gradient
            color = QColor.fromHsv(int(i / len(self.bars) * 360), 255, 255)
            painter.setPen(QPen(color))
            painter.setBrush(color)
            
            x = i * bar_width + bar_spacing
            y = self.height() // 2 - bar_height // 2
            width = bar_width - bar_spacing
            height = bar_height
            
            painter.drawRoundedRect(x, y, width, height, 5, 5)

# --- Kelas Utama Aplikasi Pemutar Audio ---
class AudioPlayer(QMainWindow):
    """
    Aplikasi pemutar audio yang stylish dengan fitur dasar.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Macan Audio Player 🎵")
        self.setGeometry(100, 100, 500, 600)
        
        # Inisialisasi QMediaPlayer dan QAudioOutput
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # State
        self.is_playing = False
        self.playlist = []
        self.current_index = -1
        
        # Inisialisasi status bar
        self.setStatusBar(QStatusBar())

        self.setup_ui()
        self.setup_connections()
        self.apply_stylesheet()
        
    def setup_ui(self):
        """
        Menyiapkan semua widget dan layout antarmuka pengguna.
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Bagian Playlist
        self.playlist_widget = QListWidget()
        self.main_layout.addWidget(self.playlist_widget)

        # Label informasi lagu
        self.track_info_label = QLabel("Tidak Ada Lagu")
        self.track_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_info_label.setObjectName("trackInfo")
        self.main_layout.addWidget(self.track_info_label)

        # Bagian Visualizer BARU
        self.visualizer_widget = VisualizerWidget()
        self.main_layout.addWidget(self.visualizer_widget)

        # Bagian Seekbar
        self.seekbar = QSlider(Qt.Orientation.Horizontal)
        self.seekbar.setRange(0, 0)
        self.seekbar.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.seekbar)
        
        # Bagian Kontrol
        self.control_panel = QHBoxLayout()
        
        self.prev_button = QPushButton("⏮️")
        self.play_pause_button = QPushButton("▶️")
        self.stop_button = QPushButton("⏹️")
        self.next_button = QPushButton("⏭️")
        self.add_folder_button = QPushButton("Tambah Folder")
        
        self.control_panel.addWidget(self.prev_button)
        self.control_panel.addWidget(self.play_pause_button)
        self.control_panel.addWidget(self.stop_button)
        self.control_panel.addWidget(self.next_button)
        self.control_panel.addWidget(self.add_folder_button)
        
        # Bagian Kontrol Volume
        self.volume_label = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100) # Atur volume default ke 100%
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)

        self.main_layout.addLayout(self.control_panel)
        self.main_layout.addLayout(volume_layout)
        
    def setup_connections(self):
        """
        Menghubungkan sinyal-sinyal dari widget ke slot/fungsi.
        """
        self.play_pause_button.clicked.connect(self.play_pause_music)
        self.stop_button.clicked.connect(self.stop_music)
        self.next_button.clicked.connect(self.next_track)
        self.prev_button.clicked.connect(self.prev_track)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.playlist_widget.doubleClicked.connect(self.play_selected_track)
        
        # Koneksi sinyal dari media player
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        
        # Koneksi sinyal untuk kontrol volume
        self.volume_slider.valueChanged.connect(self.set_volume)
        
    def play_pause_music(self):
        """
        Memulai atau menghentikan pemutaran lagu.
        """
        if not self.playlist:
            QMessageBox.information(self, "Informasi", "Silakan tambahkan lagu terlebih dahulu.")
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_pause_button.setText("▶️")
            self.is_playing = False
            self.visualizer_widget.stop() # Hentikan visualizer
        else:
            if self.current_index == -1:
                # Jika belum ada lagu yang dipilih, putar lagu pertama
                self.current_index = 0
                self.play_current_track()
            else:
                self.player.play()
            self.play_pause_button.setText("⏸️")
            self.is_playing = True
            self.visualizer_widget.start() # Mulai visualizer

    def stop_music(self):
        """
        Menghentikan pemutaran lagu.
        """
        self.player.stop()
        self.play_pause_button.setText("▶️")
        self.is_playing = False
        self.track_info_label.setText("Tidak Ada Lagu")
        self.visualizer_widget.stop() # Hentikan visualizer

    def next_track(self):
        """
        Memutar lagu berikutnya dalam playlist.
        """
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current_track()

    def prev_track(self):
        """
        Memutar lagu sebelumnya dalam playlist.
        """
        if not self.playlist: return
        self.current_index = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
        self.play_current_track()

    def add_folder(self):
        """
        Membuka dialog untuk menambahkan folder berisi file audio ke playlist.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Musik")
        if folder_path:
            self.playlist.clear()
            self.playlist_widget.clear()
            
            supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
            for filename in os.listdir(folder_path):
                if any(filename.endswith(ext) for ext in supported_formats):
                    full_path = os.path.join(folder_path, filename)
                    self.playlist.append(full_path)
                    self.playlist_widget.addItem(filename)
            
            if self.playlist:
                self.current_index = 0
                self.statusBar().showMessage(f"Ditemukan {len(self.playlist)} lagu.")
                self.playlist_widget.setCurrentRow(0)

    def play_selected_track(self):
        """
        Memutar lagu yang dipilih dari playlist.
        """
        self.current_index = self.playlist_widget.currentRow()
        self.play_current_track()

    def play_current_track(self):
        """
        Memutar lagu yang saat ini dipilih.
        """
        if self.current_index >= 0 and self.current_index < len(self.playlist):
            track_path = self.playlist[self.current_index]
            self.player.setSource(QUrl.fromLocalFile(track_path))
            self.player.play()
            self.play_pause_button.setText("⏸️")
            self.is_playing = True
            
            # Update label informasi lagu
            track_name = os.path.basename(track_path)
            self.track_info_label.setText(track_name)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start() # Mulai visualizer
            
    def update_position(self, position):
        """
        Memperbarui posisi seekbar saat lagu diputar.
        """
        if not self.seekbar.isSliderDown():
            self.seekbar.setValue(position)

    def update_duration(self, duration):
        """
        Memperbarui rentang seekbar saat lagu baru dimuat.
        """
        self.seekbar.setRange(0, duration)

    def set_position(self, position):
        """
        Mengatur posisi pemutaran lagu saat seekbar digeser.
        """
        self.player.setPosition(position)
        
    def set_volume(self, value):
        """
        Mengatur volume audio berdasarkan nilai slider.
        """
        self.audio_output.setVolume(value / 100.0)
        
    def handle_media_status(self, status):
        """
        Mengelola status media untuk transisi otomatis ke lagu berikutnya.
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track()

    def apply_stylesheet(self):
        """
        Menerapkan stylesheet (QSS) untuk desain premium dan estetik.
        """
        qss = """
            QMainWindow {
                background-color: #121212;
                color: #ffffff;
            }
            QWidget#central_widget {
                background-color: #1a1a1a;
                border-radius: 10px;
                margin: 10px;
                padding: 10px;
            }
            QLabel#trackInfo {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
            }
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: #e0e0e0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #555555;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #333333;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #1db954; /* Warna hijau Spotify */
                border: 1px solid #1db954;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #1db954;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #333333;
                border: none;
                color: #ffffff;
                padding: 12px;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QMessageBox {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QStatusBar {
                color: #a0a0a0;
                background-color: #1a1a1a;
                border-top: 1px solid #333333;
            }
        """
        self.setStyleSheet(qss)

# --- Titik Masuk Aplikasi ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = AudioPlayer()
    player.show()
    sys.exit(app.exec())
