# Nama file: macan_audio_player_equalizer_qsettings.py
# Jalankan dengan perintah: python macan_audio_player_equalizer_qsettings.py
#
# Pastikan pustaka yang dibutuhkan sudah terinstal:
# pip install PyQt6
# pip install PyQt6-QtMultimedia
#
# Perubahan: Ditambahkan fitur penyimpanan playlist otomatis menggunakan QSettings.
# Playlist sekarang akan dimuat saat aplikasi dimulai dan disimpan saat ditutup.

import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QStatusBar, QDialog, QGridLayout, QMenu, QMenuBar
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize, QSettings
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# --- Kelas Widget Visualizer ---
class VisualizerWidget(QWidget):
    """
    Widget kustom untuk menggambar visualizer audio yang disimulasikan.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.bars = [0] * 50
        self.equalizer_settings = {'bass': 0, 'mid': 0, 'treble': 0}
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        
    def start(self):
        """Memulai animasi visualizer."""
        self.timer.start(50)

    def stop(self):
        """Menghentikan animasi visualizer."""
        self.timer.stop()
        self.bars = [0] * 50
        self.update()

    def set_equalizer_settings(self, settings):
        """Menerima dan menyimpan pengaturan equalizer baru."""
        self.equalizer_settings = settings

    def update_bars(self):
        """Memperbarui tinggi bar secara acak untuk simulasi,
           dengan pengaruh dari pengaturan equalizer."""
        num_bars = len(self.bars)
        
        for i in range(num_bars):
            base_height = random.randint(1, self.height() // 2)
            
            if i < num_bars / 3:
                eq_mod = self.equalizer_settings['bass'] / 100.0
                modified_height = base_height * (1 + eq_mod)
            elif i < num_bars * 2 / 3:
                eq_mod = self.equalizer_settings['mid'] / 100.0
                modified_height = base_height * (1 + eq_mod)
            else:
                eq_mod = self.equalizer_settings['treble'] / 100.0
                modified_height = base_height * (1 + eq_mod)
            
            self.bars[i] = int(modified_height)
            
        self.update()

    def paintEvent(self, event):
        """Fungsi utama untuk menggambar visualizer."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        bar_width = self.width() // len(self.bars)
        bar_spacing = 2
        
        for i, bar_height in enumerate(self.bars):
            color = QColor.fromHsv(int(i / len(self.bars) * 360), 255, 255)
            painter.setPen(QPen(color))
            painter.setBrush(color)
            
            x = i * bar_width + bar_spacing
            y = self.height() // 2 - bar_height // 2
            width = bar_width - bar_spacing
            height = bar_height
            
            painter.drawRoundedRect(x, y, width, height, 5, 5)

# --- Kelas Dialog Equalizer ---
class EqualizerDialog(QDialog):
    """
    Dialog untuk mengatur Equalizer.
    """
    equalizer_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None, initial_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Equalizer")
        self.setFixedSize(300, 200)
        self.equalizer_settings = initial_settings or {'bass': 0, 'mid': 0, 'treble': 0}

        self.setup_ui()
        self.setup_connections()
        self.apply_stylesheet()

    def setup_ui(self):
        """Menyiapkan UI untuk dialog equalizer."""
        main_layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        self.bass_label = QLabel("Bass")
        self.bass_slider = QSlider(Qt.Orientation.Vertical)
        self.bass_slider.setRange(-100, 100)
        self.bass_slider.setValue(self.equalizer_settings['bass'])
        self.bass_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.bass_slider.setTickInterval(50)
        
        grid_layout.addWidget(self.bass_slider, 0, 0)
        grid_layout.addWidget(self.bass_label, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.mid_label = QLabel("Mid")
        self.mid_slider = QSlider(Qt.Orientation.Vertical)
        self.mid_slider.setRange(-100, 100)
        self.mid_slider.setValue(self.equalizer_settings['mid'])
        self.mid_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.mid_slider.setTickInterval(50)
        
        grid_layout.addWidget(self.mid_slider, 0, 1)
        grid_layout.addWidget(self.mid_label, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.treble_label = QLabel("Treble")
        self.treble_slider = QSlider(Qt.Orientation.Vertical)
        self.treble_slider.setRange(-100, 100)
        self.treble_slider.setValue(self.equalizer_settings['treble'])
        self.treble_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.treble_slider.setTickInterval(50)
        
        grid_layout.addWidget(self.treble_slider, 0, 2)
        grid_layout.addWidget(self.treble_label, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addLayout(grid_layout)

    def setup_connections(self):
        """Menghubungkan sinyal slider ke pembaruan."""
        self.bass_slider.valueChanged.connect(self.update_settings)
        self.mid_slider.valueChanged.connect(self.update_settings)
        self.treble_slider.valueChanged.connect(self.update_settings)
        
    def update_settings(self):
        """Mengambil nilai slider dan memancarkan sinyal."""
        self.equalizer_settings['bass'] = self.bass_slider.value()
        self.equalizer_settings['mid'] = self.mid_slider.value()
        self.equalizer_settings['treble'] = self.treble_slider.value()
        self.equalizer_updated.emit(self.equalizer_settings)
        
    def apply_stylesheet(self):
        """Menerapkan stylesheet untuk dialog equalizer."""
        qss = """
            QDialog {
                background-color: #2a2a2a;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                padding-top: 10px;
            }
            QSlider::groove:vertical {
                border: 1px solid #444444;
                width: 8px;
                background: #333333;
                margin: 0 2px;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #1db954;
                border: 1px solid #1db954;
                height: 18px;
                margin: 0 -5px;
                border-radius: 9px;
            }
            QSlider::sub-page:vertical {
                background: #1db954;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(qss)

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
        
        # Inisialisasi QSettings untuk penyimpanan data
        # "MacanCorp" adalah nama organisasi, "MacanAudioPlayer" adalah nama aplikasi.
        self.settings = QSettings("MacanCorp", "MacanAudioPlayer")
        
        # State
        self.is_playing = False
        self.playlist = []
        self.current_index = -1
        self.equalizer_settings = {'bass': 0, 'mid': 0, 'treble': 0}
        
        self.setStatusBar(QStatusBar())

        self.setup_ui()
        self.setup_connections()
        self.apply_stylesheet()
        
        # Muat playlist dan equalizer saat aplikasi dimulai
        self.load_settings()
        
    def setup_ui(self):
        """
        Menyiapkan semua widget dan layout antarmuka pengguna.
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_menu_bar()

        self.playlist_widget = QListWidget()
        self.main_layout.addWidget(self.playlist_widget)

        self.track_info_label = QLabel("Tidak Ada Lagu")
        self.track_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_info_label.setObjectName("trackInfo")
        self.main_layout.addWidget(self.track_info_label)

        self.visualizer_widget = VisualizerWidget()
        self.main_layout.addWidget(self.visualizer_widget)

        self.seekbar = QSlider(Qt.Orientation.Horizontal)
        self.seekbar.setRange(0, 0)
        self.seekbar.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.seekbar)
        
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
        
        self.volume_label = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)

        self.main_layout.addLayout(self.control_panel)
        self.main_layout.addLayout(volume_layout)
        
    def create_menu_bar(self):
        """Membuat menu bar dengan opsi baru."""
        menu_bar = self.menuBar()

        options_menu = menu_bar.addMenu("Opsi")
        equalizer_action = QAction("Equalizer", self)
        equalizer_action.triggered.connect(self.show_equalizer_dialog)
        options_menu.addAction(equalizer_action)

    def show_equalizer_dialog(self):
        """Menampilkan dialog equalizer."""
        eq_dialog = EqualizerDialog(self, self.equalizer_settings)
        eq_dialog.equalizer_updated.connect(self.update_equalizer_settings)
        eq_dialog.exec()

    def update_equalizer_settings(self, settings):
        """Menerima pengaturan equalizer baru dari dialog dan menerapkannya."""
        self.equalizer_settings = settings
        self.visualizer_widget.set_equalizer_settings(settings)
        self.statusBar().showMessage("Equalizer Updated!")

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
        
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        
        self.volume_slider.valueChanged.connect(self.set_volume)
        
    def load_settings(self):
        """
        Memuat pengaturan dari QSettings saat aplikasi dimulai.
        """
        # Muat playlist
        loaded_playlist = self.settings.value("playlist", [], type=list)
        if loaded_playlist:
            # Filter file yang sudah tidak ada
            valid_playlist = [path for path in loaded_playlist if os.path.exists(path)]
            self.playlist = valid_playlist
            
            for track_path in self.playlist:
                self.playlist_widget.addItem(os.path.basename(track_path))
                
            if self.playlist:
                self.current_index = 0
                self.statusBar().showMessage(f"Playlist dimuat: {len(self.playlist)} lagu.")
                self.playlist_widget.setCurrentRow(0)
                
        # Muat pengaturan equalizer
        eq_settings = self.settings.value("equalizer", self.equalizer_settings, type=dict)
        self.equalizer_settings = eq_settings
        self.visualizer_widget.set_equalizer_settings(self.equalizer_settings)
        
        # Muat volume
        volume = self.settings.value("volume", 100, type=int)
        self.volume_slider.setValue(volume)
        self.audio_output.setVolume(volume / 100.0)

    def closeEvent(self, event):
        """
        Menyimpan pengaturan ke QSettings saat aplikasi ditutup.
        """
        # Simpan playlist
        self.settings.setValue("playlist", self.playlist)
        # Simpan pengaturan equalizer
        self.settings.setValue("equalizer", self.equalizer_settings)
        # Simpan volume
        self.settings.setValue("volume", self.volume_slider.value())
        
        self.player.stop()
        event.accept()

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
            self.visualizer_widget.stop()
        else:
            if self.current_index == -1 and self.playlist:
                self.current_index = 0
                self.play_current_track()
            else:
                self.player.play()
            self.play_pause_button.setText("⏸️")
            self.is_playing = True
            self.visualizer_widget.start()

    def stop_music(self):
        """
        Menghentikan pemutaran lagu.
        """
        self.player.stop()
        self.play_pause_button.setText("▶️")
        self.is_playing = False
        self.track_info_label.setText("Tidak Ada Lagu")
        self.visualizer_widget.stop()

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
                self.statusBar().showMessage(f"Ditemukan {len(self.playlist)} lagu. Playlist disimpan.")
                self.playlist_widget.setCurrentRow(0)
                
                # Simpan playlist ke QSettings
                self.settings.setValue("playlist", self.playlist)

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
            
            track_name = os.path.basename(track_path)
            self.track_info_label.setText(track_name)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start()
            
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
                background: #1db954;
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
