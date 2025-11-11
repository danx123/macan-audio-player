# macan_radio.py

import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QListWidget, QLineEdit, QLabel, QSlider, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl, QPoint, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Menggunakan data SVG ikon dari file utama untuk konsistensi
# Cukup salin bagian yang relevan untuk jendela radio
SVG_ICONS = {
    "play": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxwb2x5Z29uIHBvaW50cz0iNSAzIDE5IDEyIDUgMjEgNSAzIj48L3BvbHlnb24+PC9zdmc+",
    "stop": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxyZWN0IHg9IjYiIHk9IjYiIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiI+PC9yZWN0Pjwvc3ZnPg==",
    "close": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSIxOCIgeTE9IjYiIHgyPSI2IiB5Mj0iMTgiPjwvbGluZT48bGluZSB4MT0iNiIgeTE9IjYiIHgyPSIxOCIgeTI9IjE4Ij48L2xpbmU+PC9zdmc+",
    "volume-high": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PHBhdGggZD0iTTE1LjU0IDguNDZhNSA1IDAgMCAxIDAgNy4wNyI+PC9wYXRoPjwvc3ZnPg==",
}

# Fungsi helper untuk ikon SVG, disalin dari file utama
def get_icon_from_svg(svg_data_base64, color="#E0E0E0"):
    import base64
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QPixmap, QPainter
    try:
        svg_data_str = base64.b64decode(svg_data_base64).decode('utf-8')
        svg_data_colored = svg_data_str.replace('currentColor', color)
        renderer = QSvgRenderer(svg_data_colored.encode('utf-8'))
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon()

class RadioWindow(QDialog):
    # Sinyal untuk memberitahu pemutar utama agar berhenti sejenak
    radio_playing = pyqtSignal()

    def __init__(self, parent=None, initial_theme=None):
        super().__init__(parent)
        self.drag_pos = QPoint()
        self.stations = []
        self.current_theme_dict = initial_theme

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Radio Online Indonesia")
        self.setObjectName("radioDialog")
        self.setFixedSize(400, 500)

        # Player khusus untuk radio
        self.player = QMediaPlayer(self)
        self.player.mediaStatusChanged.connect(self.update_status_on_media_change)
        self.player.error.connect(lambda: self.show_error("Gagal memutar stasiun radio. URL mungkin tidak valid."))

        self.setup_ui()
        if self.current_theme_dict:
            self.apply_stylesheet(self.current_theme_dict)

        self.fetch_stations()

    def setup_ui(self):
        self.container = QWidget(self)
        self.container.setObjectName("container")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(1, 1, 1, 1)
        container_layout.setSpacing(0)
        
        # --- Title Bar ---
        self.title_bar = self.create_title_bar()
        container_layout.addWidget(self.title_bar)
        
        # --- Content ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cari nama radio atau kota...")
        self.search_bar.setObjectName("searchBar")
        self.search_bar.textChanged.connect(self.filter_stations)
        
        self.station_list_widget = QListWidget()
        self.station_list_widget.setObjectName("stationListWidget")
        self.station_list_widget.itemDoubleClicked.connect(self.play_selected_station)
        
        self.status_label = QLabel("Pilih stasiun radio untuk diputar.")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)

        controls_layout = self.create_controls_layout()

        content_layout.addWidget(self.search_bar)
        content_layout.addWidget(self.station_list_widget)
        content_layout.addWidget(self.status_label)
        content_layout.addLayout(controls_layout)
        
        container_layout.addLayout(content_layout)

    def create_title_bar(self):
        title_bar_widget = QWidget()
        title_bar_widget.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(title_bar_widget)
        title_bar_layout.setContentsMargins(15, 0, 5, 0)
        
        title_label = QLabel("Radio Online")
        title_label.setObjectName("titleLabel")
        
        close_button = QPushButton()
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(36, 36)
        close_button.clicked.connect(self.close)
        self.close_button_ref = close_button # Simpan referensi

        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_button)
        return title_bar_widget

    def create_controls_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.play_stop_button = QPushButton()
        self.play_stop_button.setObjectName("mainButton")
        self.play_stop_button.setFixedSize(50, 50)
        self.play_stop_button.clicked.connect(self.play_stop_radio)
        
        volume_icon = QLabel()
        volume_icon.setPixmap(get_icon_from_svg(SVG_ICONS["volume-high"]).pixmap(QSize(24, 24)))
        self.volume_icon_ref = volume_icon # Simpan referensi
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.player.setVolume)

        layout.addWidget(self.play_stop_button)
        layout.addStretch()
        layout.addWidget(volume_icon)
        layout.addWidget(self.volume_slider)
        return layout

    def fetch_stations(self):
        self.status_label.setText("Mengambil daftar stasiun radio...")
        QApplication.processEvents()
        
        # API dari radio-browser.info, difilter untuk negara Indonesia (ID)
        url = "https://de1.api.radio-browser.info/json/stations/bycountrycodeexact/ID"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.stations = response.json()
            # Filter stasiun yang punya URL stream valid
            self.stations = [s for s in self.stations if s.get('url_resolved')]
            self.stations.sort(key=lambda x: x['name']) # Urutkan berdasarkan nama
            self.populate_station_list()
            self.status_label.setText("Siap. Pilih stasiun untuk diputar.")
        except requests.exceptions.RequestException as e:
            self.show_error(f"Gagal mengambil daftar radio. Periksa koneksi internet Anda.\nError: {e}")
            self.status_label.setText("Gagal memuat daftar radio.")

    def populate_station_list(self):
        self.station_list_widget.clear()
        for station in self.stations:
            # Tampilkan nama dan kota jika tersedia
            city = station.get('state', '').strip()
            display_text = station['name']
            if city:
                display_text += f" - {city}"
            self.station_list_widget.addItem(display_text)

    def filter_stations(self, text):
        query = text.lower()
        for i in range(len(self.stations)):
            station = self.stations[i]
            item = self.station_list_widget.item(i)
            
            station_name = station.get('name', '').lower()
            station_city = station.get('state', '').lower()
            
            if query in station_name or query in station_city:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def play_selected_station(self, item):
        index = self.station_list_widget.row(item)
        self.play_radio_at_index(index)
        
    def play_stop_radio(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        else:
            current_row = self.station_list_widget.currentRow()
            if current_row >= 0:
                self.play_radio_at_index(current_row)
            else:
                self.show_error("Pilih stasiun radio dari daftar terlebih dahulu.")

    def play_radio_at_index(self, index):
        # Cari station yang sesuai dengan index di list widget (karena ada filter)
        visible_stations = [(i, station) for i, station in enumerate(self.stations) if not self.station_list_widget.item(i).isHidden()]
        
        original_index = -1
        if 0 <= index < len(visible_stations):
             original_index, station_data = visible_stations[index]
        else:
            return

        stream_url = station_data.get('url_resolved')
        if not stream_url:
            self.show_error("Stasiun ini tidak memiliki URL stream yang valid.")
            return
            
        self.radio_playing.emit() # Beri sinyal ke player utama
        self.player.setMedia(QMediaContent(QUrl(stream_url)))
        self.player.play()
        self.status_label.setText(f"Memutar: {station_data['name']}")

    def update_status_on_media_change(self, status):
        if status == QMediaPlayer.BufferingMedia:
            self.status_label.setText("Buffering...")
        elif status == QMediaPlayer.BufferedMedia:
            current_item = self.station_list_widget.currentItem()
            if current_item:
                 self.status_label.setText(f"Memutar: {current_item.text()}")
        elif status == QMediaPlayer.StalledMedia:
            self.status_label.setText("Stream terhenti. Menunggu buffer...")

        # Update ikon play/stop
        if self.player.state() == QMediaPlayer.PlayingState:
            self.play_stop_button.setIcon(get_icon_from_svg(SVG_ICONS["stop"]))
        else:
            self.play_stop_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
    
    def show_error(self, message):
        QMessageBox.warning(self, "Error", message)

    def closeEvent(self, event):
        self.player.stop()
        event.accept()

    # Fungsi untuk menangani pemindahan jendela frameless
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.drag_pos = QPoint()

    # Fungsi untuk menerapkan tema
    def apply_stylesheet(self, theme):
        self.current_theme_dict = theme
        qss = f"""
            #radioDialog, #container {{
                background-color: {theme["bg_main"]}; 
                border-radius: 12px;
                border: 1px solid {theme["border"]};
            }}
            QWidget {{ 
                color: {theme["text_primary"]}; 
                font-family: Segoe UI, sans-serif; 
                font-size: 14px; 
            }}
            #titleLabel {{ 
                font-weight: bold; 
                color: {theme["text_secondary"]}; 
            }}
            #searchBar, #stationListWidget {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                padding: 6px;
            }}
            #stationListWidget::item {{ 
                padding: 8px; 
                border-radius: 4px; 
            }}
            #stationListWidget::item:selected {{ 
                background-color: {theme["accent"]}; 
                color: #FFFFFF; 
            }}
            #stationListWidget::item:hover:!selected {{ 
                background-color: {theme["border"]}; 
            }}
            #statusLabel {{ 
                color: {theme["text_secondary"]}; 
                padding: 5px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {theme["border"]}; height: 6px; background: {theme["bg_secondary"]};
                margin: 2px 0; border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {theme["text_primary"]}; border: 1px solid {theme["text_primary"]};
                width: 14px; margin: -4px 0; border-radius: 7px;
            }}
            QSlider::handle:horizontal:hover {{ 
                background: {theme["accent"]}; 
                border: 1px solid {theme["accent"]}; 
            }}
            QSlider::sub-page:horizontal {{ 
                background: {theme["accent"]}; 
                border-radius: 3px; 
            }}
            QPushButton {{ border: none; background-color: transparent; }}
            #mainButton {{
                background-color: {theme["accent"]}; color: #FFFFFF; border-radius: 25px;
            }}
            #mainButton:hover {{ background-color: {theme["accent_hover"]}; }}
            #closeButton:hover {{ background-color: #E81123; }}
        """
        self.setStyleSheet(qss)
        
        # Perbarui ikon dengan warna tema yang benar
        text_color = theme["text_primary"]
        self.close_button_ref.setIcon(get_icon_from_svg(SVG_ICONS["close"], color=text_color))
        self.volume_icon_ref.setPixmap(get_icon_from_svg(SVG_ICONS["volume-high"], color=text_color).pixmap(QSize(24, 24)))
        self.update_status_on_media_change(self.player.mediaStatus())