import sys
import os
import random
import base64
import re
from functools import partial
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QMenu, QDialog, QGridLayout, QStatusBar, QTabWidget, QTextEdit,
    QComboBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize, QSettings, QPoint, QRect
from PyQt6.QtGui import QIcon, QPainter, QColor, QAction, QPixmap, QCursor, QTextCursor, QFont
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

# --- [AESTHETICS] DATA SVG IKON ---
SVG_ICONS = {
    "play": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlnb24gcG9pbnRzPSI1IDMgMTkgMTIgNSAyMSA1IDMiPjwvcG9seWdvbj48L3N2Zz4=",
    "pause": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iNiIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iMTYiPjwvcmVjdD48cmVjdCB4PSIxNCIgeT0iNCIgd2lkdGg9IjQiIGhlaWdodD0iMTYiPjwvcmVjdD48L3N2Zz4=",
    "next": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iNSA0IDE1IDEyIDUgMjAgNSA0Ij48L3BvbHlnb24+PGxpbmUgeDE9IjE5IiB5MT0iNSIgeDI9IjE5IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "previous": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTkgNCA5IDEyIDE5IDIwIDE5IDQiPjwvcG9seWdvbj48bGluZSB4MT0iNSIgeTE9IjUiIHgyPSI1IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "volume-high": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PHBhdGggZD0iTTE1LjU0IDguNDZhNSA1IDAgMCAxIDAgNy4wNyI+PC9wYXRoPjwvc3ZnPg==",
    "volume-muted": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PGxpbmUgeDE9IjIzIiB5MT0iOSIgeDI9IjE3IiB5Mj0iMTUiPjwvbGluZT48bGluZSB4MT0iMTciIHkxPSI5IiB4Mj0iMjMiIHkyPSIxNSI+PC9saW5lPjwvc3ZnPg==",
    "add-folder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMiAxOWEyIDIgMCAwIDEtMiAySDRhMiAyIDAgMCAxLTItMlY1YTIgMiAwIDAgMSAyLTJoNWwyIDNoOWEyIDIgMCAwIDEgMiAyeiI+PC9wYXRoPjxsaW5lIHgxPSIxMiIgeTE9IjExIiB4Mj0iMTIiIHkyPSIxNyI+PC9saW5lPjxsaW5lIHgxPSI5IiB5MT0iMTQiIHgyPSIxNSIgeTI9IjE0Ij48L2xpbmU+PC9zdmc+",
    "clear-playlist": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5bGluZSBwb2ludHM9IjMgNiA1IDYgMjEgNiI+PC9wb2x5bGluZT48cGF0aCBkPSJNMTkgNnYxNGEyIDIgMCAwIDEtMiAySDdhMiAyIDAgMCAxLTItMlY2bTMgMFY0YTIgMiAwIDAgMSAyLTJoNGEyIDIgMCAwIDEgMiAydjIiPjwvcGF0aD48L3N2Zz4=",
    "album-placeholder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM0QTQ5NDQiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIj48L2NpcmNsZT48L3N2Zz4=",
    "minimize": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSI1IiB5MT0iMTIiIHgyPSIxOSIgeTI9IjEyIj48L2xpbmU+PC9zdmc+",
    "maximize": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik04IDNINWEyIDIgMCAwIDAtMiAydjNtMTggMFY1YTIgMiAwIDAgMC0yLTJoLTNtMCAxOGgzaDJhMiAyIDAgMCAwIDItMnYtM20tMTggMHYzYTIgMiAwIDAgMCAyIDJoMyIvPjwvc3ZnPg==",
    "restore": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxyZWN0IHg9IjMiIHk9IjMiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxOCIgcng9IjIiIHJ5PSIyIiAvPjxwYXRoIGQ9Ik0xNSAzdjZhMiAyIDAgMCAxLTIgMmgtNm02LTZoLTZtNiA2djYiLz48L3N2Zz4=",
    "close": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSIxOCIgeTE9IjYiIHgyPSI2IiB5Mj0iMTgiPjwvbGluZT48bGluZSB4MT0iNiIgeTE9IjYiIHgyPSIxOCIgeTI9IjE4Ij48L2xpbmU+PC9zdmc+"
}

# --- Palet Warna untuk Tema ---
THEMES = {
    "default": {"name": "Default Dark", "accent": "#0d6efd", "accent_hover": "#0b5ed7", "bg_main": "#181818", "bg_secondary": "#121212", "border": "#2A2A2A", "text_primary": "#E0E0E0", "text_secondary": "#B0B0B0"},
    "dark_blue": {"name": "Dark Blue", "accent": "#3E82C7", "accent_hover": "#3269A1", "bg_main": "#1C2541", "bg_secondary": "#0B132B", "border": "#3A506B", "text_primary": "#FFFFFF", "text_secondary": "#D3D3D3"},
    "neon_blue": {"name": "Neon Blue", "accent": "#00E5FF", "accent_hover": "#00B8CC", "bg_main": "#0A0F1E", "bg_secondary": "#030713", "border": "#1A2B47", "text_primary": "#F0F0F0", "text_secondary": "#A0A0A0"},
    "soft_pink": {"name": "Soft Pink", "accent": "#FF8FAB", "accent_hover": "#E87A9A", "bg_main": "#3D2C3C", "bg_secondary": "#2B1E2A", "border": "#5C465B", "text_primary": "#F5E6F5", "text_secondary": "#D8C8D8"},
    "dark_sakura": {"name": "Dark Sakura", "accent": "#E6A2B3", "accent_hover": "#D18FA0", "bg_main": "#2E2226", "bg_secondary": "#1F171A", "border": "#453439", "text_primary": "#FFE8EC", "text_secondary": "#E8D3D7"},
}

def get_icon_from_svg(svg_data_base64, color="#E0E0E0"):
    try:
        svg_data_str = base64.b64decode(svg_data_base64).decode('utf-8')
        svg_data_colored = svg_data_str.replace('currentColor', color)
        renderer = QSvgRenderer(svg_data_colored.encode('utf-8'))
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon()

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            value = self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width()
            self.setValue(int(value))
            self.sliderMoved.emit(int(value))
        super().mousePressEvent(event)

class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.bars = [0] * 50
        self.equalizer_settings = {'60Hz': 0, '310Hz': 0, '1KHz': 0, '6KHz': 0, '16KHz': 0}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        self.accent_color = QColor("#0d6efd")

    def set_accent_color(self, color_hex):
        self.accent_color = QColor(color_hex)

    def start(self): self.timer.start(50)
    def stop(self):
        self.timer.stop()
        self.bars = [0] * 50
        self.update()

    def set_equalizer_settings(self, settings): self.equalizer_settings = settings

    def update_bars(self):
        num_bars = len(self.bars)
        settings_values = list(self.equalizer_settings.values())
        for i in range(num_bars):
            base_height = random.randint(1, self.height() // 2)
            band_index = min(i // (num_bars // 5), 4)
            eq_mod = settings_values[band_index] / 100.0
            self.bars[i] = int(base_height * (1 + eq_mod))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        bar_width = self.width() / len(self.bars)
        for i, bar_height in enumerate(self.bars):
            color = self.accent_color
            color.setAlphaF(0.8)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            x = i * bar_width
            y = self.height() // 2 - bar_height // 2
            height = max(1, bar_height)
            painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(height), 2, 2)

class EqualizerDialog(QDialog):
    equalizer_updated = pyqtSignal(dict)
    
    PRESETS = {
        "Flat": {'60Hz': 0, '310Hz': 0, '1KHz': 0, '6KHz': 0, '16KHz': 0},
        "Pop": {'60Hz': -10, '310Hz': 40, '1KHz': 60, '6KHz': 40, '16KHz': -10},
        "Rock": {'60Hz': 70, '310Hz': -30, '1KHz': -40, '6KHz': 40, '16KHz': 60},
        "Jazz": {'60Hz': 60, '310Hz': -20, '1KHz': -20, '6KHz': 50, '16KHz': 70},
        "Classical": {'60Hz': 80, '310Hz': 60, '1KHz': -30, '6KHz': 70, '16KHz': 70},
        "Vocal": {'60Hz': -30, '310Hz': -40, '1KHz': 50, '6KHz': 40, '16KHz': -20},
    }

    def __init__(self, parent=None, initial_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Equalizer")
        self.setObjectName("equalizerDialog")
        self.setFixedSize(400, 250)
        
        self.bands = ['60Hz', '310Hz', '1KHz', '6KHz', '16KHz']
        self.equalizer_settings = initial_settings or self.PRESETS["Flat"].copy()
        
        main_layout = QVBoxLayout(self)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.PRESETS.keys())
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        main_layout.addLayout(preset_layout)

        grid_layout = QGridLayout()
        self.sliders = {}
        for i, band_name in enumerate(self.bands):
            slider = self._create_slider(band_name, self.equalizer_settings[band_name], grid_layout, i)
            slider.valueChanged.connect(self.update_settings)
            self.sliders[band_name] = slider
        
        main_layout.addLayout(grid_layout)
        
    def _create_slider(self, name, value, layout, column):
        label = QLabel(name)
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setRange(-100, 100)
        slider.setValue(value)
        slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        slider.setTickInterval(50)
        layout.addWidget(slider, 0, column, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 1, column, Qt.AlignmentFlag.AlignCenter)
        return slider

    def _apply_preset(self, preset_name):
        settings = self.PRESETS.get(preset_name)
        if settings:
            for band_name, value in settings.items():
                self.sliders[band_name].setValue(value)
    
    def update_settings(self):
        for band_name, slider in self.sliders.items():
            self.equalizer_settings[band_name] = slider.value()
        self.equalizer_updated.emit(self.equalizer_settings)
        current_preset = self.preset_combo.currentText()
        if self.equalizer_settings != self.PRESETS.get(current_preset):
            if self.preset_combo.findText("Custom") == -1:
                self.preset_combo.addItem("Custom")
            self.preset_combo.setCurrentText("Custom")

class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        self.setAcceptDrops(True)

        self.setWindowTitle("Macan Audio Player 🎵")
        self.setGeometry(100, 100, 850, 650)
        self.setMinimumSize(600, 450)
        
        self.drag_pos = QPoint()
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 5

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self.settings = QSettings("MacanCorp", "MacanAudioPlayerResizable")
        self.playlist = []
        self.current_index = -1
        self.is_muted = False
        self.last_volume = 100
        self.equalizer_settings = {'60Hz': 0, '310Hz': 0, '1KHz': 0, '6KHz': 0, '16KHz': 0}
        self.current_theme = "default"
        
        self.lyrics_data = []
        self.current_lyric_index = -1
        
        # [BARU] Variabel untuk auto-resume
        self.resume_position = -1
        
        self.setup_ui()
        self.setup_connections()
        self.load_settings()

    def setup_ui(self):
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setMouseTracking(True)
        self.setCentralWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)
        
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)

        main_layout.addLayout(self.create_title_bar())
        
        main_content_layout = QHBoxLayout()
        main_content_layout.setContentsMargins(20, 10, 20, 20)
        main_content_layout.setSpacing(20)

        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(15)
        
        left_panel_layout.addLayout(self.create_info_panel())
        left_panel_layout.addLayout(self.create_seekbar_panel())
        left_panel_layout.addLayout(self.create_playback_controls())
        left_panel_layout.addLayout(self.create_bottom_panel())
        
        left_widget = QWidget()
        left_widget.setLayout(left_panel_layout)
        
        self.right_tabs = QTabWidget()
        self.right_tabs.setObjectName("rightTabs")

        self.playlist_widget = QListWidget()
        self.playlist_widget.setObjectName("playlistWidget")
        self.playlist_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.playlist_widget.viewport().setAcceptDrops(True)
        self.playlist_widget.setDropIndicatorShown(True)

        self.lyrics_widget = QWidget()
        lyrics_layout = QVBoxLayout(self.lyrics_widget)
        lyrics_layout.setContentsMargins(0, 0, 0, 0)
        self.lyrics_status_label = QLabel("Lirik tidak ditemukan.")
        self.lyrics_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lyrics_viewer = QTextEdit()
        self.lyrics_viewer.setObjectName("lyricsViewer")
        self.lyrics_viewer.setReadOnly(True)
        lyrics_layout.addWidget(self.lyrics_status_label)
        lyrics_layout.addWidget(self.lyrics_viewer)
        self.lyrics_viewer.hide()

        self.right_tabs.addTab(self.playlist_widget, "Playlist")
        self.right_tabs.addTab(self.lyrics_widget, "Lirik")
        
        main_content_layout.addWidget(left_widget, 2)
        main_content_layout.addWidget(self.right_tabs, 1)

        main_layout.addLayout(main_content_layout)
        
        self.update_status_bar()

    def create_title_bar(self):
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(15, 0, 5, 0)
        
        self.title_label = QLabel("Macan Audio Player 🎵")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setFixedHeight(40)
        
        self.options_button = QPushButton("...")
        self.options_button.setObjectName("iconButton")
        self.options_button.setFixedSize(36, 36)
        
        options_menu = QMenu(self)
        equalizer_action = QAction("Equalizer", self)
        equalizer_action.triggered.connect(self.show_equalizer_dialog)
        options_menu.addAction(equalizer_action)

        options_menu.addSeparator()
        theme_menu = QMenu("Tema", self)
        options_menu.addMenu(theme_menu)

        for theme_id, theme_data in THEMES.items():
            theme_action = QAction(theme_data["name"], self)
            theme_action.triggered.connect(partial(self.change_theme, theme_id))
            theme_menu.addAction(theme_action)
            
        self.options_button.setMenu(options_menu)

        title_bar_layout.addWidget(self.options_button)
        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch()

        self.minimize_button = self._create_button("minimize", "Minimize", "windowControlButton")
        self.maximize_button = self._create_button("maximize", "Maximize", "windowControlButton")
        self.close_button = self._create_button("close", "Close", "windowControlButton")
        self.close_button.setObjectName("closeButton")

        title_bar_layout.addWidget(self.minimize_button)
        title_bar_layout.addWidget(self.maximize_button)
        title_bar_layout.addWidget(self.close_button)
        
        return title_bar_layout

    def create_info_panel(self):
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        self.album_art_label = QLabel()
        self.album_art_label.setObjectName("albumArt")
        self.album_art_label.setFixedSize(250, 250)
        self.album_art_label.setScaledContents(True)
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.update_album_art(None)
        
        self.track_title_label = QLabel("Tidak Ada Lagu")
        self.track_title_label.setObjectName("trackTitle")
        self.track_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_title_label.setWordWrap(True)
        
        self.artist_label = QLabel("Pilih lagu untuk diputar")
        self.artist_label.setObjectName("artistLabel")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.visualizer_widget = VisualizerWidget()
        
        top_wrapper_layout = QHBoxLayout()
        top_wrapper_layout.addStretch()
        top_wrapper_layout.addWidget(self.album_art_label)
        top_wrapper_layout.addStretch()
        
        info_layout.addStretch()
        info_layout.addLayout(top_wrapper_layout)
        info_layout.addWidget(self.track_title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.visualizer_widget)
        info_layout.addStretch()
        
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
        button.setIcon(get_icon_from_svg(SVG_ICONS[icon_name]))
        button.setToolTip(tooltip)
        if object_name:
            button.setObjectName(object_name)
        return button

    def setup_connections(self):
        self.close_button.clicked.connect(self.close)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
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
        self.playlist_widget.model().rowsMoved.connect(self.playlist_reordered)
    
    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def event(self, event):
        if event.type() == event.Type.WindowStateChange:
            if self.isMaximized():
                self.maximize_button.setIcon(get_icon_from_svg(SVG_ICONS["restore"]))
                self.maximize_button.setToolTip("Restore")
            else:
                self.maximize_button.setIcon(get_icon_from_svg(SVG_ICONS["maximize"]))
                self.maximize_button.setToolTip("Maximize")
        return super().event(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
            new_tracks_found = False
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in supported_formats):
                        if file_path not in self.playlist:
                            self.playlist.append(file_path)
                            new_tracks_found = True
            
            if new_tracks_found:
                if self.current_index == -1 and self.playlist:
                    self.current_index = 0
                    self.update_track_info(self.playlist[0])
                self.update_playlist_display()
                self.update_status_bar()

    def set_cursor_shape(self, pos):
        if self.isMaximized():
            self.unsetCursor()
            return

        rect = self.rect()
        on_left = abs(pos.x() - rect.left()) < self.resize_margin
        on_right = abs(pos.x() - rect.right()) < self.resize_margin
        on_top = abs(pos.y() - rect.top()) < self.resize_margin
        on_bottom = abs(pos.y() - rect.bottom()) < self.resize_margin

        if (on_top and on_left) or (on_bottom and on_right):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            self.resize_edge = ('top-left' if on_top else 'bottom-right')
        elif (on_top and on_right) or (on_bottom and on_left):
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            self.resize_edge = ('top-right' if on_top else 'bottom-left')
        elif on_left or on_right:
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            self.resize_edge = ('left' if on_left else 'right')
        elif on_top or on_bottom:
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            self.resize_edge = ('top' if on_top else 'bottom')
        else:
            self.unsetCursor()
            self.resize_edge = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resize_edge is not None:
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geom = self.geometry()
            elif self.title_label.geometry().contains(event.pos()):
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.resizing:
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            new_geom = QRect(self.resize_start_geom)
            
            if 'left' in self.resize_edge:
                new_geom.setLeft(self.resize_start_geom.left() + delta.x())
            if 'right' in self.resize_edge:
                new_geom.setRight(self.resize_start_geom.right() + delta.x())
            if 'top' in self.resize_edge:
                new_geom.setTop(self.resize_start_geom.top() + delta.y())
            if 'bottom' in self.resize_edge:
                new_geom.setBottom(self.resize_start_geom.bottom() + delta.y())

            if new_geom.width() < self.minimumWidth():
                new_geom.setLeft(self.resize_start_geom.left())
            if new_geom.height() < self.minimumHeight():
                new_geom.setTop(self.resize_start_geom.top())
            
            self.setGeometry(new_geom)
        
        elif not self.drag_pos.isNull() and event.buttons() == Qt.MouseButton.LeftButton:
            if not self.isMaximized():
                self.move(event.globalPosition().toPoint() - self.drag_pos)
        
        else:
            self.set_cursor_shape(pos)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = QPoint()
        self.resizing = False
        self.resize_edge = None

    def load_settings(self):
        self.current_theme = self.settings.value("theme", "default", type=str)
        self.apply_stylesheet()
        
        loaded_playlist = self.settings.value("playlist", [], type=list)
        if loaded_playlist:
            self.playlist = [path for path in loaded_playlist if os.path.exists(path)]
        
        # [MODIFIKASI] Logika untuk auto-resume
        last_index = self.settings.value("last_index", -1, type=int)
        last_position = self.settings.value("last_position", -1, type=int)

        if self.playlist and 0 <= last_index < len(self.playlist):
            self.current_index = last_index
            track_path = self.playlist[self.current_index]
            self.update_track_info(track_path)
            self.player.setSource(QUrl.fromLocalFile(track_path))
            if last_position > 0:
                self.resume_position = last_position
        elif self.playlist:
            self.current_index = 0
            self.update_track_info(self.playlist[0])

        self.update_playlist_display()
        self.update_status_bar()
        
        eq_settings = self.settings.value("equalizer", self.equalizer_settings, type=dict)
        if all(key in eq_settings for key in self.equalizer_settings.keys()):
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
        self.settings.setValue("theme", self.current_theme)

        # [BARU] Simpan status lagu terakhir untuk auto-resume
        if self.current_index != -1 and self.player.source().isValid():
            self.settings.setValue("last_index", self.current_index)
            self.settings.setValue("last_position", self.player.position())
        else:
            self.settings.remove("last_index")
            self.settings.remove("last_position")

        self.player.stop()
        event.accept()

    def play_pause_music(self):
        if not self.playlist:
            QMessageBox.information(self, "Informasi", "Playlist kosong. Silakan tambahkan lagu.")
            return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
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
            new_tracks_found = False
            # [MODIFIKASI] Gunakan os.walk() untuk pemindaian rekursif
            for root, _, files in os.walk(folder_path):
                for filename in sorted(files):
                    if any(filename.lower().endswith(ext) for ext in supported_formats):
                        full_path = os.path.join(root, filename)
                        if full_path not in self.playlist:
                            self.playlist.append(full_path)
                            new_tracks_found = True
            
            if new_tracks_found:
                if self.current_index == -1 and self.playlist:
                    self.current_index = 0
                    self.update_track_info(self.playlist[0])
                self.update_playlist_display()
                self.update_status_bar()

    def clear_playlist(self):
        self.player.stop()
        self.playlist.clear()
        self.current_index = -1
        self.reset_ui_info()
        self.visualizer_widget.stop()
        self.update_playlist_display()
        self.update_status_bar()

    def play_selected_track(self):
        self.current_index = self.playlist_widget.currentRow()
        self.play_current_track()
        
    def play_current_track(self):
        if 0 <= self.current_index < len(self.playlist):
            track_path = self.playlist[self.current_index]
            self.player.setSource(QUrl.fromLocalFile(track_path))
            self.player.play()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
            self.update_track_info(track_path)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start()
            
    def update_track_info(self, track_path):
        metadata = self.get_track_metadata(track_path)
        self.track_title_label.setText(metadata.get('title', 'Unknown Title'))
        self.artist_label.setText(metadata.get('artist', 'Unknown Artist'))
        self.update_album_art(metadata.get('artwork'))
        self.load_lyrics(track_path)

    def update_album_art(self, artwork_data):
        if not hasattr(self, 'default_album_art'):
            renderer = QSvgRenderer(base64.b64decode(SVG_ICONS["album-placeholder"]))
            self.default_album_art = QPixmap(250, 250)
            self.default_album_art.fill(Qt.GlobalColor.transparent)
            painter = QPainter(self.default_album_art)
            renderer.render(painter)
            painter.end()
        
        pixmap_to_show = self.default_album_art
        if artwork_data:
            pixmap = QPixmap()
            if pixmap.loadFromData(artwork_data):
                pixmap_to_show = pixmap
        
        self.album_art_label.setPixmap(pixmap_to_show)

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
        self.update_album_art(None)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self.seekbar.setValue(0)
        self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
        self.load_lyrics(None)

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_position(self, position):
        if not self.seekbar.isSliderDown(): self.seekbar.setValue(position)
        self.current_time_label.setText(self.format_time(position))
        self.sync_lyrics(position)

    def update_duration(self, duration):
        self.seekbar.setRange(0, duration)
        self.total_time_label.setText(self.format_time(duration))
        # [BARU] Terapkan posisi resume setelah media dimuat
        if self.resume_position != -1:
            self.set_position(self.resume_position)
            # Reset agar tidak dijalankan lagi untuk lagu berikutnya
            self.resume_position = -1

    def set_position(self, position):
        self.player.setPosition(position)
        
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
        icon_name = "volume-high" if value > 0 else "volume-muted"
        self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS[icon_name]))
        if value > 0:
            self.is_muted = False
            self.last_volume = value
        else:
            self.is_muted = True
            
    def toggle_mute(self):
        if self.is_muted:
            self.volume_slider.setValue(self.last_volume)
        else:
            current_volume = self.volume_slider.value()
            if current_volume > 0:
                self.last_volume = current_volume
            elif self.last_volume == 0:
                self.last_volume = 75
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
    
    def update_status_bar(self):
        count = len(self.playlist)
        self.status_bar.showMessage(f"{count} lagu dalam playlist")
        
    def update_playlist_display(self):
        playing_path = None
        if 0 <= self.current_index < len(self.playlist):
            playing_path = self.playlist[self.current_index]

        self.playlist_widget.clear()
        for i, track_path in enumerate(self.playlist):
            title = self.get_track_metadata(track_path).get('title', os.path.basename(track_path))
            self.playlist_widget.addItem(f"{i + 1}. {title}")
        
        if playing_path and playing_path in self.playlist:
            self.current_index = self.playlist.index(playing_path)
            self.playlist_widget.setCurrentRow(self.current_index)
            
    def playlist_reordered(self, parent, start, end, destination, row):
        if start == row: return
        
        playing_path = None
        if 0 <= self.current_index < len(self.playlist):
            playing_path = self.playlist[self.current_index]
            
        moved_item = self.playlist.pop(start)
        
        insert_pos = row
        if start < row:
            insert_pos -= 1

        self.playlist.insert(insert_pos, moved_item)
        
        if playing_path:
            try:
                self.current_index = self.playlist.index(playing_path)
            except ValueError:
                self.current_index = -1
        
        self.update_playlist_display()

    def load_lyrics(self, track_path):
        self.lyrics_data = []
        self.current_lyric_index = -1
        self.lyrics_viewer.clear()

        if not track_path:
            self.lyrics_status_label.setText("Lirik tidak tersedia.")
            self.lyrics_status_label.show()
            self.lyrics_viewer.hide()
            return

        base_path, _ = os.path.splitext(track_path)
        lrc_path = base_path + ".lrc"
        txt_path = base_path + ".txt"

        content = None
        is_lrc = False
        if os.path.exists(lrc_path):
            try:
                with open(lrc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                is_lrc = True
            except:
                pass
        elif os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                pass
        
        if content and is_lrc:
            self.parse_lrc(content)
        elif content:
            self.lyrics_data.append((0, content))
        
        if self.lyrics_data:
            self.lyrics_status_label.hide()
            self.lyrics_viewer.show()
            self.display_full_lyrics()
        else:
            self.lyrics_status_label.setText("Lirik tidak ditemukan.")
            self.lyrics_status_label.show()
            self.lyrics_viewer.hide()

    def parse_lrc(self, content):
        lrc_regex = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)')
        for line in content.splitlines():
            match = lrc_regex.match(line)
            if match:
                m, s, ms, text = match.groups()
                timestamp = int(m) * 60000 + int(s) * 1000 + int(ms)
                self.lyrics_data.append((timestamp, text.strip()))
        self.lyrics_data.sort()

    def display_full_lyrics(self):
        self.lyrics_viewer.clear()
        if not self.lyrics_data: return

        if len(self.lyrics_data) == 1 and self.lyrics_data[0][0] == 0:
            self.lyrics_viewer.setText(self.lyrics_data[0][1])
        else:
            html = "<br>".join([line[1] if line[1] else "&nbsp;" for line in self.lyrics_data])
            self.lyrics_viewer.setHtml(f"<center>{html}</center>")
    
    def sync_lyrics(self, position):
        if not self.lyrics_data or (len(self.lyrics_data) == 1 and self.lyrics_data[0][0] == 0):
            return

        found_index = -1
        for i, (timestamp, _) in enumerate(self.lyrics_data):
            if position >= timestamp:
                found_index = i
            else:
                break
        
        if found_index != self.current_lyric_index:
            self.current_lyric_index = found_index
            self.highlight_lyric_line(found_index)
            
    def highlight_lyric_line(self, line_index):
        if line_index < 0:
            return

        # Store the current scrollbar position
        vertical_scrollbar = self.lyrics_viewer.verticalScrollBar()
        current_scroll_pos = vertical_scrollbar.value()

        theme = THEMES[self.current_theme]
        html = []
        for i, (_, text) in enumerate(self.lyrics_data):
            line_text = text if text else "&nbsp;"
            if i == line_index:
                # Use a span with a specific ID to easily find it later
                html.append(f'<span id="highlighted-line" style="color:{theme["accent"]}; font-weight: bold;">{line_text}</span>')
            else:
                html.append(line_text)
        
        # Set the new HTML content
        self.lyrics_viewer.setHtml(f'<center>{"<br>".join(html)}</center>')
        
        # Find the highlighted element and scroll to it
        doc = self.lyrics_viewer.document()
        cursor = QTextCursor(doc.find('<span id="highlighted-line"'))
        if not cursor.isNull():
            self.lyrics_viewer.setTextCursor(cursor)
            self.lyrics_viewer.ensureCursorVisible()
            
        
    
    def change_theme(self, theme_id):
        self.current_theme = theme_id
        self.apply_stylesheet()
        self.settings.setValue("theme", theme_id)

    def apply_stylesheet(self):
        theme = THEMES[self.current_theme]
        self.visualizer_widget.set_accent_color(theme["accent"])

        qss = f"""
            #container {{ 
                background-color: {theme["bg_main"]}; 
                border-radius: 12px;
                border: 1px solid {theme["border"]};
            }}
            QWidget {{ color: {theme["text_primary"]}; font-family: Segoe UI, sans-serif; font-size: 14px; }}
            QMenu, QComboBox QAbstractItemView {{ background-color: {theme["bg_main"]}; border: 1px solid {theme["border"]}; }}
            QMenu::item:selected, QComboBox QAbstractItemView::item:selected {{ background-color: {theme["accent"]}; }}
            
            QComboBox {{ 
                border: 1px solid {theme["border"]}; 
                border-radius: 4px; 
                padding: 4px;
                background-color: {theme["bg_secondary"]};
            }}
            QComboBox::drop-down {{ border: none; }}

            #equalizerDialog, QDialog {{ background-color: {theme["bg_main"]}; }}

            #titleLabel {{ font-weight: bold; padding-left: 10px; color: {theme["text_secondary"]}; }}
            #albumArt {{ 
                border: 1px solid {theme["border"]}; 
                border-radius: 12px;
                background-color: {theme["bg_secondary"]};
            }}
            #trackTitle {{ font-size: 20px; font-weight: bold; color: {theme["text_primary"]}; }}
            #artistLabel {{ font-size: 15px; color: {theme["text_secondary"]}; }}
            
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 6px;
                color: {theme["text_secondary"]};
            }}
            QTabBar::tab:hover {{ background-color: {theme["border"]}; }}
            QTabBar::tab:selected {{ 
                background-color: {theme["accent"]};
                color: #FFFFFF;
            }}

            #playlistWidget, #lyricsViewer {{
                background-color: {theme["bg_secondary"]}; border: 1px solid {theme["border"]};
                border-radius: 8px; padding: 5px;
            }}
            #playlistWidget::item {{ padding: 10px; border-radius: 5px; }}
            #playlistWidget::item:selected {{ background-color: {theme["accent"]}; color: #FFFFFF; }}
            #playlistWidget::item:hover:!selected {{ background-color: {theme["border"]}; }}
            #lyricsViewer {{
                font-size: 16px;
                line-height: 150%;
            }}
            
            QSlider::groove:horizontal {{
                border: 1px solid {theme["border"]}; height: 8px; background: {theme["bg_secondary"]};
                margin: 2px 0; border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {theme["text_primary"]}; border: 1px solid {theme["text_primary"]};
                width: 16px; margin: -4px 0; border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{ background: {theme["accent"]}; border: 1px solid {theme["accent"]}; }}
            QSlider::sub-page:horizontal {{ background: {theme["accent"]}; border-radius: 4px; }}

            QSlider::groove:vertical {{
                border: 1px solid {theme["border"]}; width: 8px; background: {theme["bg_secondary"]};
                margin: 0 2px; border-radius: 4px;
            }}
            QSlider::handle:vertical {{
                background: {theme["text_primary"]}; border: 1px solid {theme["text_primary"]};
                height: 16px; margin: 0 -4px; border-radius: 8px;
            }}
            QSlider::handle:vertical:hover {{ background: {theme["accent"]}; border: 1px solid {theme["accent"]}; }}
            QSlider::sub-page:vertical {{ background: {theme["accent"]}; border-radius: 4px; }}

            QPushButton {{ border: none; background-color: transparent; }}
            #mainButton {{
                background-color: {theme["accent"]}; color: #FFFFFF; border-radius: 30px;
                min-width: 60px; min-height: 60px; padding: 8px;
            }}
            #mainButton:hover {{ background-color: {theme["accent_hover"]}; }}
            #secondaryButton {{
                background-color: transparent; border-radius: 24px;
                min-width: 48px; min-height: 48px;
            }}
            #iconButton, #windowControlButton {{
                border-radius: 18px; min-width: 36px; min-height: 36px;
            }}
            #secondaryButton:hover, #iconButton:hover, #windowControlButton:hover {{ background-color: {theme["border"]}; }}
            #closeButton:hover {{ background-color: #E81123; }}
            #mainButton:pressed, #secondaryButton:pressed, #iconButton:pressed, #windowControlButton:pressed {{ background-color: #444; }}
            
            QPushButton, QLabel {{ background-color: transparent; }}
            QStatusBar {{ color: {theme["text_secondary"]}; }}
            QStatusBar::item {{ border: none; }}
            
            QScrollBar:vertical {{
                border: none; background: {theme["bg_secondary"]}; width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {theme["border"]}; min-height: 20px; border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {theme["text_secondary"]}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """
        self.setStyleSheet(qss)
        
        text_color = theme["text_primary"]
        self.prev_button.setIcon(get_icon_from_svg(SVG_ICONS["previous"], color=text_color))
        self.next_button.setIcon(get_icon_from_svg(SVG_ICONS["next"], color=text_color))
        self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS["volume-high"], color=text_color))
        self.add_folder_button.setIcon(get_icon_from_svg(SVG_ICONS["add-folder"], color=text_color))
        self.clear_playlist_button.setIcon(get_icon_from_svg(SVG_ICONS["clear-playlist"], color=text_color))
        self.minimize_button.setIcon(get_icon_from_svg(SVG_ICONS["minimize"], color=text_color))
        self.maximize_button.setIcon(get_icon_from_svg(SVG_ICONS["maximize"], color=text_color))
        self.close_button.setIcon(get_icon_from_svg(SVG_ICONS["close"], color=text_color))
        
        self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play" if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState else "pause"]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not MUTAGEN_AVAILABLE:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText("Pustaka 'mutagen' tidak ditemukan.")
        msg_box.setInformativeText("Fitur metadata tidak akan berfungsi.\nInstall dengan: pip install mutagen")
        msg_box.setWindowTitle("Peringatan")
        msg_box.exec()

    player = AudioPlayer()
    player.show()
    sys.exit(app.exec())