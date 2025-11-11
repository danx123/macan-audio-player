import sys
import os
import random
import base64
import re
# [BARU] Impor untuk membuka lokasi file dan info sistem
import subprocess
import platform
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QListWidget, QFileDialog, QMessageBox,
    QMenu, QDialog, QGridLayout, QStatusBar, QTabWidget, QTextEdit,
    QComboBox, QLineEdit, QAction, QSystemTrayIcon, QStyle, QActionGroup,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize, QSettings, QPoint, QRect, QEvent
from PyQt5.QtGui import QCursor, QTextCursor, QPixmap, QColor, QPainter, QFont, QTextBlockFormat, QTextCharFormat, QIcon

# [FIX] Import QMediaContent untuk kompatibilitas
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from macan_audio_library import LibraryWindow
from macan_radio import RadioWindow

# [FITUR 3] Import modul khusus Windows untuk thumbnail toolbar dari PyQt5
if sys.platform == 'win32':
    try:
        from PyQt5.QtWinExtras import QWinThumbnailToolBar, QWinThumbnailToolButton
        WINDOWS_EXTRAS_AVAILABLE = True
    except ImportError:
        WINDOWS_EXTRAS_AVAILABLE = False
else:
    WINDOWS_EXTRAS_AVAILABLE = False


from PyQt5.QtSvg import QSvgRenderer

# Import pustaka untuk metadata
try:
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.m4a import M4A
    from mutagen.aac import AAC
    from mutagen.id3 import APIC
    from mutagen.ogg import OggFileType
    from mutagen.wave import WAVE
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# --- [AESTHETICS] DATA SVG IKON ---
SVG_ICONS = {
    # [FIX] SVG data for 'play' and 'pause' replaced with valid versions
    "play": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxwb2x5Z29uIHBvaW50cz0iNSAzIDE5IDEyIDUgMjEgNSAzIj48L3BvbHlnb24+PC9zdmc+",
    "pause": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxyZWN0IHg9IjYiIHk9IjQiIHdpZHRoPSI0IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PHJlY3QgeD0iMTQiIHk9IjQiIHdpZHRoPSI0IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PC9zdmc+",
    "next": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iNSA0IDE1IDEyIDUgMjAgNSA0Ij48L3BvbHlnb24+PGxpbmUgeDE9IjE5IiB5MT0iNSIgeDI9IjE5IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "previous": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTkgNCA5IDEyIDE5IDIwIDE5IDQiPjwvcG9seWdvbj48bGluZSB4MT0iNSIgeTE9IjUiIHgyPSI1IiB5Mj0iMTkiPjwvbGluZT48L3N2Zz4=",
    "volume-high": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PHBhdGggZD0iTTE1LjU0IDguNDZhNSA1IDAgMCAxIDAgNy4wNyI+PC9wYXRoPjwvc3ZnPg==",
    "volume-muted": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5Z29uIHBvaW50cz0iMTEgNSA2IDkgMiA5IDIgMTUgNiAxNSAxMSAxOSAxMSA1Ij48L3BvbHlnb24+PGxpbmUgeDE9IjIzIiB5MT0iOSIgeDI9IjE3IiB5Mj0iMTUiLz48bGluZSB4MT0iMTciIHkxPSI5IiB5Mj0iMjMiIHkyPSIxNSIvPjwvc3ZnPg==",
    "add-folder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMiAxOWEyIDIgMCAwIDEtMiAySDRhMiAyIDAgMCAxLTItMlY1YTIgMiAwIDAgMSAyLTJoNWwyIDNoOWEyIDIgMCAwIDEgMiAyeiI+PC9wYXRoPjxsaW5lIHgxPSIxMiIgeTE9IjExIiB4Mj0iMTIiIHkyPSIxNyI+PC9saW5lPjxsaW5lIHgxPSI5IiB5MT0iMTQiIHgyPSIxNSIgeTI9IjE0Ij48L2xpbmU+PC9zdmc+",
    "clear-playlist": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5bGluZSBwb2ludHM9IjMgNiA1IDYgMjEgNiI+PC9wb2x5bGluZT48cGF0aCBkPSJNMTkgNnYxNGEyIDIgMCAwIDEtMiAySDdhMiAyIDAgMCAxLTItMlY2bTMgMFY0YTIgMiAwIDAgMSAyLTJoNGEyIDIgMCAwIDEgMiAydjIiPjwvcGF0aD48L3N2Zz4=",
    "album-placeholder": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM0QTQ5NDQiIHN0cm9rZS11aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIj48L2NpcmNsZT48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIj48L2NpcmNsZT48L3N2Zz4=",
    "minimize": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSI1IiB5MT0iMTIiIHgyPSIxOSIgeTI9IjEyIj48L2xpbmU+PC9zdmc+",
    "maximize": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0zIDMgOW0wLTE4djZoLTE4di02aDE4eiIvPjxyZWN0IHg9IjMiIHk9IjMiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxOCIgcng9IjIiIHJ5PSIyIj48L3JlY3Q+PC9zdmc+",
    "restore": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik04IDNoLTRhMiAyIDAgMCAwLTIgMnYxMWEyIDIgMCAwIDAgMiAyaDExYTIgMiAwIDAgMCAyLTJ2LTQiLz48cmVjdCB4PSIxMiIgeT0iMyIgd2lkdGg9IjkiIGhlaWdodD0iOSIgcng9IjIiIHJ5PSIyIi8+PC9zdmc+",
    "close": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSIxOCIgeTE9IjYiIHgyPSI2IiB5Mj0iMTgiPjwvbGluZT48bGluZSB4MT0iNiIgeTE9IjYiIHgyPSIxOCIgeTI9IjE4Ij48L2xpbmU+PC9zdmc+",
    "shuffle": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xOCAxMEwyMiAxNEwxOCAxOCIvPjxwYXRoIGQ9Ik02IDZMMiAxMEw2IDE0Ii8+PHBhdGggZD0iTTIyIDEwSDguNUM1LjQ2IDEwIDMgMTIuNDYgMyAxNS41VjE2LjUiLz48cGF0aCBkPSJNMCAxNEgxNS41QzE4LjU0IDE0IDIxIDExLjU0IDIxIDguNVY3LjUiLz48L3N2Zz4=",
    "repeat": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNyAxbDQgNC00IDQiLz48cGF0aCBkPSJNMwoxMVY5YTQgNCAwIDAgMSA0LTRoMTQiLz48cGF0aCBkPSJNNyAyM2wtNC00IDQtNCIvPjxwYXRoIGQ9Ik0yMSAxM3YyYTQgNCAwIDAgMS00IDRIMyIvPjwvc3ZnPg==",
    "tray": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xMiAzdjEyIi8+PHBhdGggZD0ibTggMTEgNCA0IDQtNCIvPjxwYXRoIGQ9Ik0yMSAxNUgzIi8+PC9zdmc+",
    "list": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxsaW5lIHgxPSI4IiB5MT0iNiIgeDI9IjIxIiB5Mj0iNiIvPjxsaW5lIHgxPSI4IiB5MT0iMTIiIHgyPSIxMyIgeTI9IjEyIi8+PGxpbmUgeDE9IjgiIHkxPSIxOCIgeDI9IjIxIiB5Mj0iMTgiLz48bGluZSB4MT0iMyIgeTE9IjYiIHgyPSIzLjAxIiB5Mj0iNiIvPjxsaW5lIHgxPSIzIiB5MT0iMTIiIHgyPSIzLjAxIiB5Mj0iMTIiLz48bGluZSB4MT0iMyIgeTE9IjE4IiB4Mj0iMy4wMSIgeTI9IjE4Ii8+PC9zdmc+"
}

# [SKIN BARU] Ikon putih khusus untuk Toolbar Mode
SVG_ICONS_WHITE = {
    "play": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxwb2x5Z29uIHBvaW50cz0iNSAzIDE5IDEyIDUgMjEgNSAzIj48L3BvbHlnb24+PC9zdmc+",
    "pause": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJjdXJyZW50Q29sb3IiPjxyZWN0IHg9IjYiIHk9IjQiIHdpZHRoPSI0IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PHJlY3QgeD0iMTQiIHk9IjQiIHdpZHRoPSI0IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PC9zdmc+",
    "next": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWdvbiBwb2ludHM9IjUgNCAxNSAxMiA1IDIwIDUgNCI+PC9wb2x5Z29uPjxsaW5lIHgxPSIxOSIgeTE9IjUiIHgyPSIxOSIgeTI9IjE5Ij48L2xpbmU+PC9zdmc+",
    "previous": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWdvbiBwb2ludHM9IjE5IDQgOSAxMiAxOSAyMCAxOSA0Ij48L3BvbHlnb24+PGxpbmUgeDE9IjUiIHkxPSI1IiB4MiA9IjUiIHkyPSIxOSI+PC9saW5lPjwvc3ZnPg==",
    "list": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHToPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48bGluZSB4MT0iOCIgeTE9IjYiIHgyPSIyMSIgeTI9IjYiLz48bGluZSB4MT0iOCIgeTE9IjEyIiB4Mj0iMTMiIHkyPSIxMiIvPjxsaW5lIHgxPSI4IiB5MT0iMTgiIHgyPSIyMSIgeTI9IjE4Ii8+PGxpbmUgeDE9IjMiIHkxPSI2IiB4Mj0iMy4wMSIgeTI9IjYiLz48bGluZSB4MT0iMyIgeTE9IjEyIiB4Mj0iMy4wMSIgeTI9IjEyIi8+PGxpbmUgeDE9IjMiIHkxPSIxOCIgeDI9IjMuMDEiIHkyPSIxOCIvPjwvc3ZnPg==",
    "volume": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWdvbiBwb2ludHM9IjExIDUgNiA5IDIgOSAyIDE1IDYgMTUgMTEgMTkgMTEgNSI+PC9wb2x5Z29uPjxwYXRoIGQ9Ik0xNS41NCA4LjQ2YTUgNSAwIDAgMSAwIDcuMDciPjwvcGF0aD48L3N2Zz4=",
    # [FIX] Ikon baru untuk tombol opsi dan close di toolbar
    "options": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxIj48L2NpcmNsZT48Y2lyY2xlIGN4PSIxMiIgY3k9IjUiIHI9IjEiPjwvY2lyY2xlPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTkiIHI9IjEiPjwvY2lyY2xlPjwvc3ZnPg==",
    "close": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZHRoPSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48bGluZSB4MT0iMTgiIHkxPSI2IiB4Mj0iNiIgeTI9IjE4Ij48L2xpbmU+PGxpbmUgeDE9IjYiIHkxPSI2IiB4Mj0iMTgiIHkyPSIxOCI+PC9saW5lPjwvc3ZnPg=="
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
        # Ganti warna generik
        svg_data_colored = svg_data_str.replace('currentColor', color)
        # Ganti warna putih hardcode jika ada parameter warna
        if 'fill="#FFFFFF"' in svg_data_colored and color != "#E0E0E0":
             svg_data_colored = svg_data_colored.replace('fill="#FFFFFF"', f'fill="{color}"')
        if 'stroke="#FFFFFF"' in svg_data_colored and color != "#E0E0E0":
             svg_data_colored = svg_data_colored.replace('stroke="#FFFFFF"', f'stroke="{color}"')
             
        renderer = QSvgRenderer(svg_data_colored.encode('utf-8'))
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon()

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            value = self.minimum() + (self.maximum() - self.minimum()) * event.pos().x() / self.width()
            self.setValue(int(value))
            self.sliderMoved.emit(int(value))
        super().mousePressEvent(event)

class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setMinimumHeight(40)
        self.bars = [0] * 50
        self.equalizer_settings = {'60Hz': 0, '310Hz': 0, '1KHz': 0, '6KHz': 0, '16KHz': 0}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        self.accent_color = QColor("#0d6efd")
        self.visualizer_mode = 0
        self.setToolTip("Klik untuk mengubah gaya visualizer")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.visualizer_mode = (self.visualizer_mode + 1) % 3
            self.update()
        super().mousePressEvent(event)

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
            if self.visualizer_mode == 1:
                 self.bars[i] = int(base_height * (1 + eq_mod) * 2)
            else:
                 self.bars[i] = int(base_height * (1 + eq_mod))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)
        bar_width = self.width() / len(self.bars)

        for i, bar_height in enumerate(self.bars):
            color = self.accent_color
            color.setAlphaF(0.8)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            x = i * bar_width
            height = max(1, bar_height)

            if self.visualizer_mode == 0:
                y = self.height() // 2 - height // 2
                painter.drawRoundedRect(int(x), int(y), int(bar_width - 2), int(height), 2, 2)

            elif self.visualizer_mode == 1:
                y = self.height() - height
                painter.drawRect(int(x), int(y), int(bar_width - 2), int(height))

            elif self.visualizer_mode == 2:
                y_center = self.height() // 2
                painter.drawRect(int(x), y_center - height, int(bar_width - 2), int(height))
                color.setAlphaF(0.3)
                painter.setBrush(color)
                painter.drawRect(int(x), y_center, int(bar_width - 2), int(height * 0.5))


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
        icon_path = "music.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

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
        slider = QSlider(Qt.Vertical)
        slider.setRange(-100, 100)
        slider.setValue(value)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(50)
        layout.addWidget(slider, 0, column, Qt.AlignCenter)
        layout.addWidget(label, 1, column, Qt.AlignCenter)
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

class MiniPlayer(QWidget):
    def __init__(self, main_player_instance):
        super().__init__()
        self.main_player = main_player_instance
        self.drag_pos = QPoint()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("miniPlayer")
        self.setFixedSize(200, 60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.prev_button = self._create_button("previous", "Lagu Sebelumnya")
        self.play_pause_button = self._create_button("play", "Putar/Jeda")
        self.next_button = self._create_button("next", "Lagu Berikutnya")

        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)

        self.prev_button.clicked.connect(self.main_player.prev_track)
        self.play_pause_button.clicked.connect(self.main_player.play_pause_music)
        self.next_button.clicked.connect(self.main_player.next_track)

        self.main_player.playback_state_changed.connect(self.update_play_pause_icon)

    def _create_button(self, icon_name, tooltip):
        button = QPushButton()
        button.setIcon(get_icon_from_svg(SVG_ICONS[icon_name]))
        button.setToolTip(tooltip)
        button.setObjectName("miniPlayerButton")
        button.setFixedSize(40, 40)
        return button

    def update_play_pause_icon(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_pause_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
        else:
            self.play_pause_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))

    def apply_stylesheet(self, theme):
        self.setStyleSheet(f"""
            #miniPlayer {{
                background-color: {theme["bg_main"]};
                border: 1px solid {theme["border"]};
                border-radius: 30px;
            }}
            #miniPlayerButton {{
                background-color: transparent;
                border-radius: 20px;
            }}
            #miniPlayerButton:hover {{
                background-color: {theme["border"]};
            }}
            #miniPlayerButton:pressed {{
                background-color: {theme["accent"]};
            }}
        """)
        theme_color = theme["text_primary"]
        self.update_play_pause_icon(self.main_player.player.state())
        self.prev_button.setIcon(get_icon_from_svg(SVG_ICONS["previous"], theme_color))
        self.next_button.setIcon(get_icon_from_svg(SVG_ICONS["next"], theme_color))


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

# [NOTIFIKASI BARU] Class untuk notifikasi
class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("notificationWidget")

        self.container = QWidget(self)
        self.container.setObjectName("notificationContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        
        self.title_label = QLabel("Title")
        self.title_label.setObjectName("notificationTitle")
        self.artist_label = QLabel("Artist")
        self.artist_label.setObjectName("notificationArtist")
        
        container_layout.addWidget(self.title_label)
        container_layout.addWidget(self.artist_label)

        self.apply_stylesheet()

    def apply_stylesheet(self):
        # Menggunakan tema default gelap secara hardcode untuk konsistensi notifikasi
        self.setStyleSheet("""
            #notificationContainer {
                background-color: rgba(24, 24, 24, 0.9);
                border-radius: 8px;
                border: 1px solid #2A2A2A;
            }
            #notificationTitle {
                color: #E0E0E0;
                font-size: 14px;
                font-weight: bold;
            }
            #notificationArtist {
                color: #B0B0B0;
                font-size: 12px;
            }
        """)

    def show_notification(self, title, artist, screen_geometry):
        self.title_label.setText(title)
        self.artist_label.setText(artist)
        
        self.adjustSize()
        
        margin = 15
        x_pos = screen_geometry.right() - self.width() - margin
        y_pos = screen_geometry.bottom() - self.height() - margin
        
        self.move(x_pos, y_pos)
        self.show()
        
        # Sembunyikan notifikasi setelah 4 detik
        QTimer.singleShot(4000, self.close)


# [SKIN BARU] Class untuk playlist Toolbar Mode
class ToolbarPlaylist(QWidget):
    track_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = QPoint()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("toolbarPlaylist")
        
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(self.list_widget)

    def _on_item_selected(self, item):
        self.track_selected.emit(self.list_widget.row(item))

    def update_playlist(self, playlist, current_index):
        self.list_widget.clear()
        self.list_widget.addItems(playlist)
        if 0 <= current_index < self.list_widget.count():
            self.list_widget.setCurrentRow(current_index)
            
    def apply_stylesheet(self, theme):
        self.setStyleSheet(f"""
            #toolbarPlaylist {{
                background-color: {theme['bg_main']};
                border-radius: 8px;
                border: 1px solid {theme['border']};
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {theme['text_primary']};
            }}
            QListWidget::item {{ padding: 8px; border-radius: 4px; }}
            QListWidget::item:selected {{ background-color: {theme['accent']}; color: #FFFFFF; }}
            QListWidget::item:hover:!selected {{ background-color: {theme['border']}; }}
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


# [SKIN BARU & FIX] Class untuk Toolbar Mode Player
class ToolbarPlayer(QWidget):
    def __init__(self, main_player_instance):
        super().__init__()
        self.main_player = main_player_instance
        self.drag_pos = QPoint()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("toolbarPlayer")
        
        self.setup_ui()
        self.setup_connections()

        self.playlist_window = ToolbarPlaylist(self)
        self.playlist_window.track_selected.connect(self.play_track_from_playlist)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Kontrol
        self.prev_button = self._create_button("previous", "Lagu Sebelumnya")
        self.play_pause_button = self._create_button("play", "Putar/Jeda")
        self.next_button = self._create_button("next", "Lagu Berikutnya")

        # Info & Seekbar
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.title_label = QLabel("Macan Audio Player")
        self.title_label.setFixedWidth(250) # Beri ruang lebih
        self.seekbar = ClickableSlider(Qt.Horizontal)
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.seekbar)

        # Volume & Kontrol Jendela
        self.volume_icon = QLabel()
        self.volume_icon.setPixmap(get_icon_from_svg(SVG_ICONS_WHITE["volume"]).pixmap(QSize(20, 20)))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setFixedWidth(80)
        
        self.playlist_button = self._create_button("list", "Tampilkan Playlist")
        
        # [FIX] Tombol Opsi dan Close
        self.options_button = self._create_button("options", "Opsi")
        self.close_button = self._create_button("close", "Tutup Aplikasi")

        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.next_button)
        layout.addLayout(info_layout)
        layout.addWidget(self.volume_icon)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.playlist_button)
        layout.addWidget(self.options_button)
        layout.addWidget(self.close_button)

    def _create_button(self, icon_name, tooltip):
        button = QPushButton()
        button.setIcon(get_icon_from_svg(SVG_ICONS_WHITE[icon_name]))
        button.setToolTip(tooltip)
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(20, 20))
        button.setObjectName("toolbarButton")
        return button

    def setup_connections(self):
        # Kontrol dari toolbar ke main player
        self.prev_button.clicked.connect(self.main_player.prev_track)
        self.play_pause_button.clicked.connect(self.main_player.play_pause_music)
        self.next_button.clicked.connect(self.main_player.next_track)
        self.volume_slider.valueChanged.connect(self.main_player.set_volume)
        self.seekbar.sliderMoved.connect(self.main_player.set_position)
        self.playlist_button.clicked.connect(self.toggle_playlist)
        
        # [FIX] Koneksi tombol baru
        self.close_button.clicked.connect(self.main_player.close)
        self.options_button.clicked.connect(self.show_options_menu)

        # Update UI toolbar dari state main player
        self.main_player.playback_state_changed.connect(self.update_play_pause_icon)
        self.main_player.player.positionChanged.connect(self.update_position)
        self.main_player.player.durationChanged.connect(self.update_duration)
    
    # [FIX] Fungsi untuk menampilkan menu opsi
    def show_options_menu(self):
        menu = QMenu(self)
        skin_menu = menu.addMenu("Ganti Skin")
        skin_group = QActionGroup(self)

        normal_action = skin_menu.addAction("Normal Mode")
        normal_action.setCheckable(True)
        normal_action.triggered.connect(lambda: self.main_player.change_skin("normal"))
        
        compact_action = skin_menu.addAction("Compact Mode")
        compact_action.setCheckable(True)
        compact_action.triggered.connect(lambda: self.main_player.change_skin("compact"))
        
        minimal_action = skin_menu.addAction("Minimal Mode")
        minimal_action.setCheckable(True)
        minimal_action.triggered.connect(lambda: self.main_player.change_skin("minimal"))
        
        toolbar_action = skin_menu.addAction("Toolbar Mode")
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True) # Mode ini sedang aktif
        toolbar_action.triggered.connect(lambda: self.main_player.change_skin("toolbar"))

        skin_group.addAction(normal_action)
        skin_group.addAction(compact_action)
        skin_group.addAction(minimal_action)
        skin_group.addAction(toolbar_action)

        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.main_player.close)

        menu.exec_(self.options_button.mapToGlobal(QPoint(0, self.options_button.height())))

    def apply_stylesheet(self, theme):
        self.playlist_window.apply_stylesheet(theme)
        # [FIX] Menggunakan warna dari tema, bukan hardcode
        self.setStyleSheet(f"""
            #toolbarPlayer {{
                background-color: {theme['bg_main']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
            }}
            #toolbarButton {{ background: transparent; border: none; }}
            #toolbarButton:hover {{ 
                background-color: {theme['border']}; 
                border-radius: 16px; 
            }}
            QLabel {{ color: #FFFFFF; font-size: 12px; }}
            QMenu {{
                background-color: {theme['bg_main']};
                border: 1px solid {theme['border']};
                color: {theme['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {theme['accent']};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {theme['border']}; height: 4px; background: {theme['bg_secondary']};
                margin: 2px 0; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #FFF; border: 1px solid #FFF;
                width: 10px; margin: -4px 0; border-radius: 5px;
            }}
            QSlider::sub-page:horizontal {{ 
                background: {theme['accent']}; border-radius: 2px; 
            }}
        """)
    
    def update_initial_state(self):
        self.update_play_pause_icon(self.main_player.player.state())
        self.update_duration(self.main_player.player.duration())
        self.update_position(self.main_player.player.position())
        self.volume_slider.setValue(self.main_player.volume_slider.value())
        self.update_track_info()

    def update_play_pause_icon(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_pause_button.setIcon(get_icon_from_svg(SVG_ICONS_WHITE["pause"]))
        else:
            self.play_pause_button.setIcon(get_icon_from_svg(SVG_ICONS_WHITE["play"]))

    def update_position(self, position):
        if not self.seekbar.isSliderDown():
            self.seekbar.setValue(position)

    def update_duration(self, duration):
        self.seekbar.setRange(0, duration)
    
    def update_track_info(self):
        if 0 <= self.main_player.current_index < len(self.main_player.playlist):
            path = self.main_player.playlist[self.main_player.current_index]
            metadata = self.main_player.get_track_metadata(path)
            self.title_label.setText(metadata.get('title', 'Unknown Title'))
        else:
            self.title_label.setText("Macan Audio Player")

    def toggle_playlist(self):
        if self.playlist_window.isVisible():
            self.playlist_window.hide()
        else:
            playlist_titles = [self.main_player.get_track_metadata(p).get('title', os.path.basename(p)) for p in self.main_player.playlist]
            self.playlist_window.update_playlist(playlist_titles, self.main_player.current_index)
            
            toolbar_pos = self.mapToGlobal(QPoint(0, 0))
            self.playlist_window.move(toolbar_pos.x(), toolbar_pos.y() + self.height() + 5)
            self.playlist_window.show()

    def play_track_from_playlist(self, index):
        item = self.main_player.playlist_widget.item(index)
        if item:
            self.main_player.play_selected_track(self.main_player.playlist_widget.indexFromItem(item))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


class AudioPlayer(QMainWindow):
    playback_state_changed = pyqtSignal(QMediaPlayer.State)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.library_window = None
        self.radio_window = None
        self.setAcceptDrops(True)

        self.setWindowTitle("Macan Audio Player")
        self.setMinimumSize(600, 450)
        self.app_icon = QIcon()
        icon_path = "music.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
            self.setWindowIcon(self.app_icon)

        self.drag_pos = QPoint()
        self.resizing = False
        self.resize_edge = None
        self.resize_margin = 5
        self.title_bar_widget = QWidget()

        self.player = QMediaPlayer()

        self.settings = QSettings("MacanCorp", "MacanAudioPlayerResizable")
        self.playlist = []
        self.current_index = -1
        self.is_muted = False
        self.last_volume = 100
        self.equalizer_settings = {'60Hz': 0, '310Hz': 0, '1KHz': 0, '6KHz': 0, '16KHz': 0}
        self.current_theme = "default"
        self.last_opened_folder = ""

        self.is_shuffled = False
        self.repeat_mode = 0
        self.play_order = []
        self.current_play_order_index = -1

        self.is_thumb_bar_initialized = False

        self.lyrics_data = []
        self.current_lyric_index = -1

        self.normal_lyric_format = QTextCharFormat()
        self.highlighted_lyric_format = QTextCharFormat()

        self.resume_position = -1
        self.was_playing_on_close = False

        self.dynamic_aura_enabled = False
        self.current_dynamic_color = None

        # [SKIN BARU] Atribut untuk manajemen skin
        self.current_skin = "normal"
        self.previous_skin = "normal" # [BARU] Untuk menangani switch dari toolbar
        self.playlist_panel_width = 280 # Lebar panel playlist saat ditoggle
        self.skin_configs = {
            "normal": {"min_size": QSize(850, 650), "fixed": False},
            "compact": {"size": QSize(480, 520), "fixed": True},
            "minimal": {"size": QSize(480, 260), "fixed": True},
            "toolbar": {"fixed": True} # Toolbar di-handle oleh class-nya sendiri
        }
        
        # [SKIN BARU] Instance untuk Toolbar dan Notifikasi
        self.toolbar_player = None
        self.notification_widget = None


        self.setup_ui()
        self.setup_connections()

        self.center_on_screen()

        self.setup_tray_icon()

        self.load_settings()

    def showEvent(self, event):
        super().showEvent(event)
        if WINDOWS_EXTRAS_AVAILABLE and not self.is_thumb_bar_initialized:
            self.setup_thumbnail_toolbar()
            self.is_thumb_bar_initialized = True

    def center_on_screen(self):
        # [FIX] Menggunakan primaryScreen() untuk penempatan tengah yang lebih andal
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            center_point = screen_geometry.center()
            frame_geometry = self.frameGeometry()
            frame_geometry.moveCenter(center_point)
            self.move(frame_geometry.topLeft())
        else:
            # Fallback untuk sistem tanpa primary screen
            super().center()

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

        title_bar_layout = self.create_title_bar()
        self.title_bar_widget.setLayout(title_bar_layout)
        self.title_bar_widget.setFixedHeight(40)
        self.title_bar_widget.setMouseTracking(True)
        main_layout.addWidget(self.title_bar_widget)

        self.main_content_layout = QHBoxLayout()
        self.main_content_layout.setContentsMargins(20, 10, 20, 20)
        self.main_content_layout.setSpacing(20)

        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(15)

        left_panel_layout.addLayout(self.create_info_panel())
        left_panel_layout.addLayout(self.create_seekbar_panel())
        left_panel_layout.addLayout(self.create_playback_controls())
        left_panel_layout.addLayout(self.create_bottom_panel())

        left_widget = QWidget()
        left_widget.setLayout(left_panel_layout)

        self.right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(self.right_panel_widget)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(10)

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("Find song on playlist...")

        self.right_tabs = QTabWidget()
        self.right_tabs.setObjectName("rightTabs")

        self.playlist_widget = QListWidget()
        self.playlist_widget.setObjectName("playlistWidget")
        self.playlist_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_widget.setDragDropMode(QListWidget.InternalMove)
        self.playlist_widget.viewport().setAcceptDrops(True)
        self.playlist_widget.setDropIndicatorShown(True)

        self.lyrics_widget = QWidget()
        lyrics_layout = QVBoxLayout(self.lyrics_widget)
        lyrics_layout.setContentsMargins(0, 0, 0, 0)
        self.lyrics_status_label = QLabel("Lirik tidak ditemukan.")
        self.lyrics_status_label.setAlignment(Qt.AlignCenter)
        self.lyrics_viewer = QTextEdit()
        self.lyrics_viewer.setObjectName("lyricsViewer")
        self.lyrics_viewer.setReadOnly(True)
        lyrics_layout.addWidget(self.lyrics_status_label)
        lyrics_layout.addWidget(self.lyrics_viewer)
        self.lyrics_viewer.hide()

        self.right_tabs.addTab(self.playlist_widget, "Playlist")
        self.right_tabs.addTab(self.lyrics_widget, "Lirik")

        right_panel_layout.addWidget(self.search_bar)
        right_panel_layout.addWidget(self.right_tabs)

        self.main_content_layout.addWidget(left_widget, 2)
        self.main_content_layout.addWidget(self.right_panel_widget, 1)

        main_layout.addLayout(self.main_content_layout)

        self.update_status_bar()

    def create_title_bar(self):
        title_bar_layout = QHBoxLayout()
        title_bar_layout.setContentsMargins(15, 0, 5, 0)

        self.title_label = QLabel("Macan Audio Player")
        self.title_label.setObjectName("titleLabel")

        self.options_button = QPushButton("...")
        self.options_button.setObjectName("iconButton")
        self.options_button.setFixedSize(36, 36)

        options_menu = QMenu(self)

        load_playlist_action = options_menu.addAction("Load Playlist (.m3u)")
        load_playlist_action.triggered.connect(self.load_playlist_from_file)
        save_playlist_action = options_menu.addAction("Save Playlist (.m3u)")
        save_playlist_action.triggered.connect(self.save_playlist_to_file)
        options_menu.addSeparator()

        equalizer_action = options_menu.addAction("Equalizer")
        equalizer_action.triggered.connect(self.show_equalizer_dialog)

        library_action = options_menu.addAction("Music Library")
        library_action.triggered.connect(self.show_library_window)

        radio_action = options_menu.addAction("Radio Online")
        radio_action.triggered.connect(self.show_radio_window)

        options_menu.addSeparator()

        self.dynamic_aura_action = options_menu.addAction("Dynamic Aura")
        self.dynamic_aura_action.setCheckable(True)
        self.dynamic_aura_action.toggled.connect(self.toggle_dynamic_aura)

        # [SKIN BARU] Membuat menu Skin
        skin_menu = options_menu.addMenu("Skin")
        skin_group = QActionGroup(self)
        skin_group.setExclusive(True)

        self.normal_skin_action = skin_group.addAction(skin_menu.addAction("Normal Mode"))
        self.normal_skin_action.setCheckable(True)
        self.normal_skin_action.triggered.connect(lambda: self.change_skin("normal"))

        self.compact_skin_action = skin_group.addAction(skin_menu.addAction("Compact Mode"))
        self.compact_skin_action.setCheckable(True)
        self.compact_skin_action.triggered.connect(lambda: self.change_skin("compact"))

        self.minimal_skin_action = skin_group.addAction(skin_menu.addAction("Minimal Mode"))
        self.minimal_skin_action.setCheckable(True)
        self.minimal_skin_action.triggered.connect(lambda: self.change_skin("minimal"))
        
        # [SKIN BARU] Opsi untuk Toolbar Mode
        self.toolbar_skin_action = skin_group.addAction(skin_menu.addAction("Toolbar Mode"))
        self.toolbar_skin_action.setCheckable(True)
        self.toolbar_skin_action.triggered.connect(lambda: self.change_skin("toolbar"))

        options_menu.addSeparator()

        theme_menu = options_menu.addMenu("Theme")
        for theme_id, theme_data in THEMES.items():
            theme_action = theme_menu.addAction(theme_data["name"])
            theme_action.triggered.connect(partial(self.change_theme, theme_id))

        options_menu.addSeparator()

        about_action = options_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

        exit_action = options_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        self.options_button.setMenu(options_menu)

        title_bar_layout.addWidget(self.options_button)
        title_bar_layout.addWidget(self.title_label)
        title_bar_layout.addStretch()

        self.tray_button = self._create_button("tray", "Minimize to Tray", "windowControlButton")
        self.minimize_button = self._create_button("minimize", "Minimize", "windowControlButton")
        self.maximize_button = self._create_button("maximize", "Maximize", "windowControlButton")
        self.close_button = self._create_button("close", "Close", "windowControlButton")
        self.close_button.setObjectName("closeButton")

        title_bar_layout.addWidget(self.tray_button)
        title_bar_layout.addWidget(self.minimize_button)
        title_bar_layout.addWidget(self.maximize_button)
        title_bar_layout.addWidget(self.close_button)

        return title_bar_layout

    def show_about_dialog(self):
        about_text = """<b>Macan Audio Player</b>
        <p>Macan Audio Player is a modern audio player designed to deliver the best music experience with an elegant touch..</p>
        <p>Powered by PyQt5 and FFmpeg, this application supports various popular audio formats with light, fast, and stable performance.</p>
        <p>© 2025 - Danx Exodus</p>"""
        QMessageBox.about(self, "About", about_text)

    def create_info_panel(self):
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        self.album_art_label = QLabel()
        self.album_art_label.setObjectName("albumArt")
        self.album_art_label.setFixedSize(250, 250)
        self.album_art_label.setScaledContents(True)
        self.album_art_label.setAlignment(Qt.AlignCenter)
        self.update_album_art(None)

        self.track_title_label = QLabel("Tidak Ada Lagu")
        self.track_title_label.setObjectName("trackTitle")
        self.track_title_label.setAlignment(Qt.AlignCenter)
        self.track_title_label.setWordWrap(True)

        self.artist_label = QLabel("Pilih lagu untuk diputar")
        self.artist_label.setObjectName("artistLabel")
        self.artist_label.setAlignment(Qt.AlignCenter)

        self.visualizer_widget = VisualizerWidget()

        # [SKIN BARU] Bungkus album art dalam widget agar mudah disembunyikan
        self.album_art_container_widget = QWidget()
        top_wrapper_layout = QHBoxLayout(self.album_art_container_widget)
        top_wrapper_layout.setContentsMargins(0,0,0,0)
        top_wrapper_layout.addStretch()
        top_wrapper_layout.addWidget(self.album_art_label)
        top_wrapper_layout.addStretch()

        info_layout.addStretch()
        info_layout.addWidget(self.album_art_container_widget)
        info_layout.addWidget(self.track_title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.visualizer_widget)
        info_layout.addStretch()

        return info_layout

    def create_seekbar_panel(self):
        seekbar_layout = QVBoxLayout()
        seekbar_layout.setSpacing(5)
        self.seekbar = ClickableSlider(Qt.Horizontal)
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
        control_layout.setSpacing(15)

        self.shuffle_button = self._create_button("shuffle", "Acak (Mati)", "secondaryButton")
        self.prev_button = self._create_button("previous", "Lagu Sebelumnya", "secondaryButton")
        self.play_button = self._create_button("play", "Putar", "mainButton", use_theme_color=True)
        self.next_button = self._create_button("next", "Lagu Berikutnya", "secondaryButton")
        self.repeat_button = self._create_button("repeat", "Ulangi (Mati)", "secondaryButton")

        control_layout.addStretch()
        control_layout.addWidget(self.shuffle_button)
        control_layout.addWidget(self.prev_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.repeat_button)
        control_layout.addStretch()
        return control_layout

    def create_bottom_panel(self):
        bottom_layout = QHBoxLayout()
        self.volume_button = self._create_button("volume-high", "Mute/Unmute", "iconButton")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setFixedWidth(120)

        bottom_layout.addWidget(self.volume_button)
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addStretch()

        # [SKIN BARU] Tombol untuk menampilkan/menyembunyikan playlist
        self.toggle_playlist_button = self._create_button("list", "Tampilkan/Sembunyikan Playlist", "iconButton")

        self.add_folder_button = self._create_button("add-folder", "Tambah Folder", "iconButton")
        self.clear_playlist_button = self._create_button("clear-playlist", "Bersihkan Playlist", "iconButton")

        bottom_layout.addWidget(self.toggle_playlist_button)
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

    def setup_thumbnail_toolbar(self):
        self.thumb_bar = QWinThumbnailToolBar(self)
        self.thumb_bar.setWindow(self.windowHandle())

        self.prev_thumb_button = QWinThumbnailToolButton(self)
        self.prev_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["previous"]))
        self.prev_thumb_button.setToolTip("Lagu Sebelumnya")
        self.prev_thumb_button.clicked.connect(self.prev_track)

        self.play_pause_thumb_button = QWinThumbnailToolButton(self)
        self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
        self.play_pause_thumb_button.setToolTip("Putar")
        self.play_pause_thumb_button.clicked.connect(self.play_pause_music)

        self.next_thumb_button = QWinThumbnailToolButton(self)
        self.next_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["next"]))
        self.next_thumb_button.setToolTip("Lagu Berikutnya")
        self.next_thumb_button.clicked.connect(self.next_track)

        self.thumb_bar.addButton(self.prev_thumb_button)
        self.thumb_bar.addButton(self.play_pause_thumb_button)
        self.thumb_bar.addButton(self.next_thumb_button)

    def setup_tray_icon(self):
        self.mini_player = MiniPlayer(self)

        self.tray_icon = QSystemTrayIcon(self.app_icon, self)
        self.tray_icon.setToolTip("Macan Audio Player")

        tray_menu = QMenu()
        restore_action = tray_menu.addAction("Show Player")
        restore_action.triggered.connect(self.restore_from_tray)

        tray_menu.addSeparator()

        tray_play_pause_action = tray_menu.addAction("Play/Pause")
        tray_play_pause_action.triggered.connect(self.play_pause_music)
        tray_next_action = tray_menu.addAction("Next")
        tray_next_action.triggered.connect(self.next_track)
        tray_prev_action = tray_menu.addAction("Previous")
        tray_prev_action.triggered.connect(self.prev_track)

        tray_menu.addSeparator()

        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def setup_connections(self):
        self.close_button.clicked.connect(self.close)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.tray_button.clicked.connect(self.minimize_to_tray)

        self.play_button.clicked.connect(self.play_pause_music)
        self.next_button.clicked.connect(self.next_track)
        self.prev_button.clicked.connect(self.prev_track)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.clear_playlist_button.clicked.connect(self.clear_playlist)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.repeat_button.clicked.connect(self.toggle_repeat)
        self.toggle_playlist_button.clicked.connect(self.toggle_playlist_visibility) # [SKIN BARU]

        self.playlist_widget.doubleClicked.connect(self.play_selected_track)
        self.playlist_widget.model().rowsMoved.connect(self.playlist_reordered)
        self.playlist_widget.customContextMenuRequested.connect(self.show_playlist_context_menu)
        self.search_bar.textChanged.connect(self.filter_playlist)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.player.stateChanged.connect(self.playback_state_changed.emit)

        self.seekbar.sliderMoved.connect(self.set_position)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_button.clicked.connect(self.toggle_mute)

    def show_playlist_context_menu(self, position):
        item = self.playlist_widget.itemAt(position)
        if not item:
            return
        menu = QMenu(self)
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(self.show_track_properties)
        menu.addAction(properties_action)
        open_location_action = QAction("Open File Location", self)
        open_location_action.triggered.connect(self.open_file_location)
        menu.addAction(open_location_action)
        menu.exec_(self.playlist_widget.mapToGlobal(position))

    def show_track_properties(self):
        index = self.playlist_widget.currentRow()
        if index < 0: return
        path = self.playlist[index]
        try:
            metadata = self.get_track_metadata(path)
            file_size_mb = os.path.getsize(path) / (1024 * 1024)
            duration_str = "N/A"
            try:
                audio_info = None
                if path.lower().endswith('.mp3'): audio_info = MP3(path)
                elif path.lower().endswith('.flac'): audio_info = FLAC(path)
                elif path.lower().endswith('.m4a'): audio_info = M4A(path)
                elif path.lower().endswith('.wav'): audio_info = WAVE(path)
                if audio_info:
                    duration_sec = int(audio_info.info.length)
                    minutes, seconds = divmod(duration_sec, 60)
                    duration_str = f"{minutes}:{seconds:02}"
            except Exception: pass
            info_text = f"""
            <b>File:</b> {os.path.basename(path)}<br>
            <b>Title:</b> {metadata.get('title', 'N/A')}<br>
            <b>Artist:</b> {metadata.get('artist', 'N/A')}<br>
            <hr>
            <b>Location:</b> {path}<br>
            <b>Size:</b> {file_size_mb:.2f} MB<br>
            <b>Duration:</b> {duration_str}<br>
            """
            QMessageBox.information(self, "Track Properties", info_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Tidak dapat membaca properti file:\n{e}")

    def open_file_location(self):
        index = self.playlist_widget.currentRow()
        if index < 0: return
        path = self.playlist[index]
        system = platform.system()
        try:
            if system == "Windows":
                # [FIX] Menggunakan os.path.normpath untuk memastikan format path benar untuk Windows Explorer
                win_path = os.path.normpath(path)
                subprocess.Popen(f'explorer /select,"{win_path}"')
            elif system == "Darwin": # macOS
                subprocess.Popen(["open", "-R", path])
            else: # Linux
                directory = os.path.dirname(path)
                subprocess.Popen(["xdg-open", directory])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Tidak dapat membuka lokasi file:\n{e}")

    def minimize_to_tray(self):
        self.hide()
        if self.toolbar_player:
            self.toolbar_player.hide()
            
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry() if screen else QApplication.desktop().availableGeometry()
        player_size = self.mini_player.size()
        margin = 15
        x_pos = screen_geometry.right() - player_size.width() - margin
        y_pos = screen_geometry.bottom() - player_size.height() - margin
        self.mini_player.move(x_pos, y_pos)
        self.mini_player.show()
        self.tray_icon.show()

    def restore_from_tray(self):
        if self.current_skin == "toolbar" and self.toolbar_player:
            self.toolbar_player.show()
            self.toolbar_player.activateWindow()
        else:
            self.showNormal()
            self.activateWindow()
        self.mini_player.hide()
        self.tray_icon.hide()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick: self.restore_from_tray()

    def toggle_maximize_restore(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def event(self, event):
        if event.type() == QEvent.WindowStateChange:
            is_maximized = self.isMaximized()
            self.maximize_button.setIcon(get_icon_from_svg(SVG_ICONS["restore" if is_maximized else "maximize"]))
            self.maximize_button.setToolTip("Restore" if is_maximized else "Maximize")
            # [SKIN BARU] Nonaktifkan skin mode jika di-maximize
            if is_maximized and self.current_skin != "normal":
                self.change_skin("normal", force=True)

        return super().event(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls: return
        supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".mp4"]
        paths_to_add = []
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if os.path.isdir(file_path):
                    for root, _, files in os.walk(file_path):
                        for filename in sorted(files):
                            if any(filename.lower().endswith(ext) for ext in supported_formats):
                                full_path = os.path.join(root, filename)
                                if full_path not in self.playlist and full_path not in paths_to_add:
                                    paths_to_add.append(full_path)
                elif os.path.isfile(file_path) and any(file_path.lower().endswith(ext) for ext in supported_formats):
                    if file_path not in self.playlist and file_path not in paths_to_add:
                        paths_to_add.append(file_path)
        if paths_to_add:
            self.playlist.extend(paths_to_add)
            self.regenerate_play_order()
            if self.current_index == -1 and self.playlist:
                self.current_index = 0
                self.current_play_order_index = 0
                self.update_track_info(self.playlist[0])
            self.update_playlist_display()
            self.update_status_bar()

    def set_cursor_shape(self, pos):
        if self.isMaximized() or self.skin_configs.get(self.current_skin, {}).get("fixed", False):
            self.unsetCursor()
            return

        rect = self.rect()
        on_left = abs(pos.x() - rect.left()) < self.resize_margin
        on_right = abs(pos.x() - rect.right()) < self.resize_margin
        on_top = abs(pos.y() - rect.top()) < self.resize_margin
        on_bottom = abs(pos.y() - rect.bottom()) < self.resize_margin

        if (on_top and on_left) or (on_bottom and on_right): self.setCursor(QCursor(Qt.SizeFDiagCursor)); self.resize_edge = ('top-left' if on_top else 'bottom-right')
        elif (on_top and on_right) or (on_bottom and on_left): self.setCursor(QCursor(Qt.SizeBDiagCursor)); self.resize_edge = ('top-right' if on_top else 'bottom-left')
        elif on_left or on_right: self.setCursor(QCursor(Qt.SizeHorCursor)); self.resize_edge = ('left' if on_left else 'right')
        elif on_top or on_bottom: self.setCursor(QCursor(Qt.SizeVerCursor)); self.resize_edge = ('top' if on_top else 'bottom')
        else: self.unsetCursor(); self.resize_edge = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos_in_title_bar = self.title_bar_widget.mapFrom(self, event.pos())
            is_on_button = any(btn.geometry().contains(pos_in_title_bar) for btn in [self.options_button, self.tray_button, self.minimize_button, self.maximize_button, self.close_button])
            if self.resize_edge is not None:
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_geom = self.geometry()
            elif self.title_bar_widget.rect().contains(pos_in_title_bar) and not is_on_button:
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.resizing:
            delta = event.globalPos() - self.resize_start_pos
            new_geom = QRect(self.resize_start_geom)
            if 'left' in self.resize_edge: new_geom.setLeft(self.resize_start_geom.left() + delta.x())
            if 'right' in self.resize_edge: new_geom.setRight(self.resize_start_geom.right() + delta.x())
            if 'top' in self.resize_edge: new_geom.setTop(self.resize_start_geom.top() + delta.y())
            if 'bottom' in self.resize_edge: new_geom.setBottom(self.resize_start_geom.bottom() + delta.y())
            if new_geom.width() < self.minimumWidth(): new_geom.setLeft(self.resize_start_geom.left())
            if new_geom.height() < self.minimumHeight(): new_geom.setTop(self.resize_start_geom.top())
            self.setGeometry(new_geom)
        elif not self.drag_pos.isNull() and event.buttons() == Qt.LeftButton:
            if not self.isMaximized(): self.move(event.globalPos() - self.drag_pos)
        else: self.set_cursor_shape(pos)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = QPoint(); self.resizing = False; self.resize_edge = None

    def load_settings(self):
        self.current_theme = self.settings.value("theme", "default", type=str)

        self.dynamic_aura_enabled = self.settings.value("dynamic_aura", False, type=bool)
        self.dynamic_aura_action.setChecked(self.dynamic_aura_enabled)

        self.apply_current_visuals()

        self.last_opened_folder = self.settings.value("last_folder", "", type=str)
        self.visualizer_widget.visualizer_mode = self.settings.value("visualizer_mode", 0, type=int)
        self.visualizer_widget.update()

        loaded_playlist = self.settings.value("playlist", [], type=list)
        if loaded_playlist: self.playlist = [path for path in loaded_playlist if os.path.exists(path)]

        self.is_shuffled = self.settings.value("shuffle_state", False, type=bool)
        self.repeat_mode = self.settings.value("repeat_mode", 0, type=int)
        self.regenerate_play_order()
        self.update_shuffle_repeat_style()

        last_index = self.settings.value("last_index", -1, type=int)
        last_position = self.settings.value("last_position", -1, type=int)
        self.was_playing_on_close = self.settings.value("was_playing", False, type=bool)

        if self.playlist and 0 <= last_index < len(self.playlist):
            self.current_index = last_index
            try: self.current_play_order_index = self.play_order.index(self.current_index)
            except ValueError:
                self.regenerate_play_order()
                self.current_play_order_index = self.play_order.index(self.current_index)
            track_path = self.playlist[self.current_index]
            self.update_track_info(track_path)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(track_path)))
            if last_position > 0: self.resume_position = last_position
        elif self.playlist:
            self.current_index = 0
            self.current_play_order_index = 0
            self.update_track_info(self.playlist[0])

        self.update_playlist_display()
        self.update_status_bar()

        eq_settings = self.settings.value("equalizer", self.equalizer_settings)
        if eq_settings and all(key in eq_settings for key in self.equalizer_settings.keys()):
            self.equalizer_settings = eq_settings
        self.visualizer_widget.set_equalizer_settings(self.equalizer_settings)

        volume = self.settings.value("volume", 100, type=int)
        self.last_volume = volume
        self.volume_slider.setValue(volume)
        self.player.setVolume(volume)

        # [SKIN BARU] Memuat skin
        saved_skin = self.settings.value("skin", "normal", type=str)
        self.change_skin(saved_skin, force=True) # Paksa apply saat startup

    def closeEvent(self, event):
        self.settings.setValue("last_folder", self.last_opened_folder)
        self.settings.setValue("visualizer_mode", self.visualizer_widget.visualizer_mode)
        self.settings.setValue("playlist", self.playlist)
        self.settings.setValue("equalizer", self.equalizer_settings)
        self.settings.setValue("volume", self.volume_slider.value())
        self.settings.setValue("theme", self.current_theme)
        self.settings.setValue("dynamic_aura", self.dynamic_aura_enabled)
        self.settings.setValue("shuffle_state", self.is_shuffled)
        self.settings.setValue("repeat_mode", self.repeat_mode)
        
        # [SKIN BARU] Simpan skin (jangan simpan 'toolbar' sebagai state default)
        skin_to_save = self.current_skin if self.current_skin != 'toolbar' else self.previous_skin
        self.settings.setValue("skin", skin_to_save)

        if self.current_index != -1 and self.player.media().canonicalUrl().isValid():
            self.settings.setValue("last_index", self.current_index)
            self.settings.setValue("last_position", self.player.position())
            self.settings.setValue("was_playing", self.player.state() == QMediaPlayer.PlayingState)
        else:
            self.settings.remove("last_index")
            self.settings.remove("last_position")
            self.settings.remove("was_playing")

        self.player.stop()
        if self.library_window: self.library_window.save_data()
        self.mini_player.close()
        if self.toolbar_player: self.toolbar_player.close() # [SKIN BARU]
        if self.radio_window: self.radio_window.close()
        self.tray_icon.hide()
        QApplication.instance().quit()
        event.accept()

    def add_and_play_paths(self, paths):
        supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
        new_tracks = [os.path.abspath(p) for p in paths if os.path.exists(p) and any(p.lower().endswith(ext) for ext in supported_formats) and os.path.abspath(p) not in self.playlist]
        if not new_tracks: return
        self.playlist.extend(new_tracks)
        self.regenerate_play_order()
        self.update_playlist_display()
        self.update_status_bar()
        self.current_index = len(self.playlist) - len(new_tracks)
        try: self.current_play_order_index = self.play_order.index(self.current_index)
        except ValueError:
             self.regenerate_play_order()
             self.current_play_order_index = self.play_order.index(self.current_index)
        self.play_current_track()

    def play_pause_music(self):
        if not self.playlist:
            QMessageBox.information(self, "Informasi", "Playlist kosong. Silakan tambahkan lagu.")
            return
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
            self.visualizer_widget.stop()
            if WINDOWS_EXTRAS_AVAILABLE and self.is_thumb_bar_initialized:
                self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
                self.play_pause_thumb_button.setToolTip("Putar")
        else:
            if self.current_index == -1:
                self.current_index = self.play_order[0] if self.play_order else 0
                self.current_play_order_index = 0
            self.play_current_track()

    def next_track(self):
        if not self.playlist or not self.play_order: return
        self.current_play_order_index = (self.current_play_order_index + 1) % len(self.play_order)
        self.current_index = self.play_order[self.current_play_order_index]
        self.play_current_track()

    def prev_track(self):
        if not self.playlist or not self.play_order: return
        self.current_play_order_index = (self.current_play_order_index - 1 + len(self.play_order)) % len(self.play_order)
        self.current_index = self.play_order[self.current_play_order_index]
        self.play_current_track()

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Musik", self.last_opened_folder)
        if folder_path:
            self.last_opened_folder = folder_path
            supported_formats = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".mp4"]
            new_tracks_found = False
            for root, _, files in os.walk(folder_path):
                for filename in sorted(files):
                    if any(filename.lower().endswith(ext) for ext in supported_formats):
                        full_path = os.path.join(root, filename)
                        if full_path not in self.playlist:
                            self.playlist.append(full_path)
                            new_tracks_found = True
            if new_tracks_found:
                self.regenerate_play_order()
                if self.current_index == -1 and self.playlist:
                    self.current_index = 0
                    self.current_play_order_index = 0
                    self.update_track_info(self.playlist[0])
                self.update_playlist_display()
                self.update_status_bar()

    def clear_playlist(self):
        self.player.stop()
        self.playlist.clear()
        self.play_order.clear()
        self.current_index = -1
        self.current_play_order_index = -1
        self.reset_ui_info()
        self.visualizer_widget.stop()
        self.update_playlist_display()
        self.update_status_bar()
        self.current_dynamic_color = None
        self.apply_current_visuals()
        if WINDOWS_EXTRAS_AVAILABLE and self.is_thumb_bar_initialized:
            self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
            self.play_pause_thumb_button.setToolTip("Putar")

    def play_selected_track(self, index):
        self.current_index = index.row()
        try: self.current_play_order_index = self.play_order.index(self.current_index)
        except ValueError:
            self.regenerate_play_order()
            self.current_play_order_index = self.play_order.index(self.current_index)
        self.play_current_track()

    def play_current_track(self):
        if 0 <= self.current_index < len(self.playlist):
            track_path = self.playlist[self.current_index]
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(track_path)))
            self.player.play()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
            self.update_track_info(track_path)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.visualizer_widget.start()
            
            if self.toolbar_player:
                self.toolbar_player.update_track_info()

            metadata = self.get_track_metadata(track_path)
            self.show_notification(metadata.get('title', 'Unknown Title'), metadata.get('artist', 'Unknown Artist'))

            if WINDOWS_EXTRAS_AVAILABLE and self.is_thumb_bar_initialized:
                self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
                self.play_pause_thumb_button.setToolTip("Jeda")
    
    def show_notification(self, title, artist):
        screen = QApplication.primaryScreen()
        if not screen: return
        
        if self.notification_widget is None:
            self.notification_widget = NotificationWidget()
            
        self.notification_widget.show_notification(title, artist, screen.availableGeometry())

    def update_track_info(self, track_path):
        metadata = self.get_track_metadata(track_path)
        artwork = metadata.get('artwork')
        if self.dynamic_aura_enabled: self.current_dynamic_color = self.extract_dominant_color(artwork)
        self.track_title_label.setText(metadata.get('title', 'Unknown Title'))
        self.artist_label.setText(metadata.get('artist', 'Unknown Artist'))
        self.update_album_art(artwork)
        self.load_lyrics(track_path)
        self.apply_current_visuals()

    def update_album_art(self, artwork_data):
        if not hasattr(self, 'default_album_art'):
            renderer = QSvgRenderer(base64.b64decode(SVG_ICONS["album-placeholder"]))
            self.default_album_art = QPixmap(250, 250)
            self.default_album_art.fill(Qt.transparent)
            painter = QPainter(self.default_album_art)
            renderer.render(painter)
            painter.end()
        pixmap_to_show = self.default_album_art
        if artwork_data:
            pixmap = QPixmap()
            if pixmap.loadFromData(artwork_data): pixmap_to_show = pixmap
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
                    if isinstance(tag, APIC): metadata['artwork'] = tag.data; break
            elif path.lower().endswith('.flac'):
                audio = FLAC(path)
                metadata['title'] = audio.get('title', [metadata['title']])[0]
                metadata['artist'] = audio.get('artist', [metadata['artist']])[0]
                if audio.pictures: metadata['artwork'] = audio.pictures[0].data
            elif path.lower().endswith(('.m4a', '.mp4')):
                audio = MP4(path)
                tags = audio.tags
                if tags:
                    metadata['title'] = tags.get('\xa9nam', [metadata['title']])[0]
                    metadata['artist'] = tags.get('\xa9ART', [metadata['artist']])[0]
                    if 'covr' in tags and tags['covr']: metadata['artwork'] = tags['covr'][0]
        except Exception: pass
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
        seconds = ms // 1000; minutes = seconds // 60; seconds %= 60
        return f"{minutes:02}:{seconds:02}"

    def update_position(self, position):
        if not self.seekbar.isSliderDown(): self.seekbar.setValue(position)
        self.current_time_label.setText(self.format_time(position))
        self.sync_lyrics(position)

    def update_duration(self, duration):
        self.seekbar.setRange(0, duration)
        self.total_time_label.setText(self.format_time(duration))
        if self.resume_position != -1:
            self.set_position(self.resume_position)
            if self.was_playing_on_close:
                self.player.play()
                self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
                self.visualizer_widget.start()
                if WINDOWS_EXTRAS_AVAILABLE and self.is_thumb_bar_initialized:
                    self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["pause"]))
                    self.play_pause_thumb_button.setToolTip("Jeda")
                self.was_playing_on_close = False
            self.resume_position = -1

    def set_position(self, position): self.player.setPosition(position)

    def set_volume(self, value):
        self.player.setVolume(value)
        icon_name = "volume-high" if value > 0 else "volume-muted"
        theme_color = THEMES[self.current_theme]['text_primary']
        self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS[icon_name], color=theme_color))
        if value > 0: self.is_muted = False; self.last_volume = value
        else: self.is_muted = True

    def toggle_mute(self):
        if self.is_muted: self.volume_slider.setValue(self.last_volume)
        else:
            current_volume = self.volume_slider.value()
            if current_volume > 0: self.last_volume = current_volume
            elif self.last_volume == 0: self.last_volume = 75
            self.volume_slider.setValue(0)

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.repeat_mode == 2: self.player.setPosition(0); self.player.play()
            elif self.repeat_mode == 1: self.next_track()
            else:
                is_last_song = self.current_play_order_index >= len(self.play_order) - 1
                if not is_last_song: self.next_track()
                else:
                    self.player.stop()
                    self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
                    self.visualizer_widget.stop()
                    if WINDOWS_EXTRAS_AVAILABLE and self.is_thumb_bar_initialized:
                        self.play_pause_thumb_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
                        self.play_pause_thumb_button.setToolTip("Putar")

    def show_equalizer_dialog(self):
        eq_dialog = EqualizerDialog(self, self.equalizer_settings)
        eq_dialog.equalizer_updated.connect(self.update_equalizer_settings)
        eq_dialog.exec_()

    def update_equalizer_settings(self, settings):
        self.equalizer_settings = settings
        self.visualizer_widget.set_equalizer_settings(settings)

    def update_status_bar(self): self.status_bar.showMessage(f"{len(self.playlist)} lagu dalam playlist")

    def update_playlist_display(self):
        playing_path = self.playlist[self.current_index] if 0 <= self.current_index < len(self.playlist) else None
        self.playlist_widget.clear()
        for i, track_path in enumerate(self.playlist):
            title = self.get_track_metadata(track_path).get('title', os.path.basename(track_path))
            self.playlist_widget.addItem(f"{i + 1}. {title}")
        if playing_path and playing_path in self.playlist:
            self.current_index = self.playlist.index(playing_path)
            self.playlist_widget.setCurrentRow(self.current_index)

    def playlist_reordered(self, parent, start, end, destination, row):
        if start == row: return
        moved_item = self.playlist.pop(start)
        insert_pos = row - 1 if start < row else row
        self.playlist.insert(insert_pos, moved_item)
        self.regenerate_play_order()
        self.update_playlist_display()

    def regenerate_play_order(self):
        n = len(self.playlist)
        current_song_path = self.playlist[self.current_index] if 0 <= self.current_index < n else None
        if self.is_shuffled:
            self.play_order = list(range(n))
            random.shuffle(self.play_order)
            if current_song_path:
                original_index = self.playlist.index(current_song_path)
                try:
                    shuffled_position = self.play_order.index(original_index)
                    current_play_order_pos = self.current_play_order_index if 0 <= self.current_play_order_index < n else 0
                    self.play_order[current_play_order_pos], self.play_order[shuffled_position] = self.play_order[shuffled_position], self.play_order[current_play_order_pos]
                except (ValueError, IndexError): self.current_play_order_index = 0
            else: self.current_play_order_index = 0 if n > 0 else -1
        else:
            self.play_order = list(range(n))
            if current_song_path: self.current_play_order_index = self.playlist.index(current_song_path)
            else: self.current_play_order_index = 0 if n > 0 else -1

    def toggle_shuffle(self):
        self.is_shuffled = not self.is_shuffled
        self.regenerate_play_order()
        self.update_shuffle_repeat_style()
        self.shuffle_button.setToolTip(f"Acak ({'Aktif' if self.is_shuffled else 'Mati'})")

    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        tooltips = ["Ulangi (Mati)", "Ulangi (Semua)", "Ulangi (Satu Lagu)"]
        self.repeat_button.setToolTip(tooltips[self.repeat_mode])
        self.update_shuffle_repeat_style()

    def update_shuffle_repeat_style(self):
        self.shuffle_button.setProperty("active", self.is_shuffled)
        self.repeat_button.setProperty("active", self.repeat_mode != 0)
        self.repeat_button.setProperty("repeat_one", self.repeat_mode == 2)
        for btn in [self.shuffle_button, self.repeat_button]:
            btn.style().unpolish(btn); btn.style().polish(btn)

    def filter_playlist(self, text):
        query = text.lower()
        for i in range(len(self.playlist)):
            item = self.playlist_widget.item(i)
            track_path = self.playlist[i]
            file_name = os.path.basename(track_path).lower()
            metadata = self.get_track_metadata(track_path)
            metadata_title = metadata.get('title', '').lower()
            metadata_artist = metadata.get('artist', '').lower()
            if query in file_name or query in metadata_title or query in metadata_artist: item.setHidden(False)
            else: item.setHidden(True)

    def save_playlist_to_file(self):
        if not self.playlist:
            QMessageBox.warning(self, "Playlist Empty", "No songs to save.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Playlist", self.last_opened_folder, "M3U Playlist (*.m3u)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for track in self.playlist: f.write(track + '\n')
                self.status_bar.showMessage(f"Playlist saved to {os.path.basename(file_path)}", 5000)
            except Exception as e: QMessageBox.critical(self, "Error", f"Gagal menyimpan playlist:\n{e}")

    def load_playlist_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Playlist", self.last_opened_folder, "M3U Playlist (*.m3u)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f: paths = [line.strip() for line in f.readlines()]
                self.clear_playlist()
                self.playlist = [path for path in paths if os.path.exists(path)]
                self.regenerate_play_order()
                if self.playlist:
                    self.current_index = 0
                    self.current_play_order_index = 0
                    self.update_track_info(self.playlist[0])
                self.update_playlist_display()
                self.update_status_bar()
                self.status_bar.showMessage(f"Playlist {os.path.basename(file_path)} loaded", 5000)
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to load playlist:\n{e}")

    def load_lyrics(self, track_path):
        self.lyrics_data = []
        self.current_lyric_index = -1
        self.lyrics_viewer.clear()
        if not track_path:
            self.lyrics_status_label.setText("Lyrics not available."); self.lyrics_status_label.show(); self.lyrics_viewer.hide()
            return
        base_path, _ = os.path.splitext(track_path)
        lrc_path = base_path + ".lrc"; txt_path = base_path + ".txt"
        content = None; is_lrc = False
        if os.path.exists(lrc_path):
            try:
                with open(lrc_path, 'r', encoding='utf-8') as f: content = f.read()
                is_lrc = True
            except: pass
        elif os.path.exists(txt_path):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f: content = f.read()
            except: pass
        if content and is_lrc: self.parse_lrc(content)
        elif content: self.lyrics_data.append((0, content))
        if self.lyrics_data:
            self.lyrics_status_label.hide(); self.lyrics_viewer.show(); self.display_full_lyrics()
        else:
            self.lyrics_status_label.setText("Lyrics not found."); self.lyrics_status_label.show(); self.lyrics_viewer.hide()

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
        cursor = self.lyrics_viewer.textCursor()
        block_format = QTextBlockFormat(); block_format.setAlignment(Qt.AlignCenter); cursor.setBlockFormat(block_format)
        if len(self.lyrics_data) == 1 and self.lyrics_data[0][0] == 0:
            cursor.insertText(self.lyrics_data[0][1], self.normal_lyric_format)
        else:
            for _, text in self.lyrics_data: cursor.insertText((text if text else "") + '\n', self.normal_lyric_format)
            cursor.deletePreviousChar()
        self.lyrics_viewer.moveCursor(QTextCursor.Start)

    def sync_lyrics(self, position):
        if not self.lyrics_data or (len(self.lyrics_data) == 1 and self.lyrics_data[0][0] == 0): return
        found_index = -1
        for i, (timestamp, _) in enumerate(self.lyrics_data):
            if position >= timestamp: found_index = i
            else: break
        if found_index != self.current_lyric_index:
            self.highlight_lyric_line(self.current_lyric_index, found_index)
            self.current_lyric_index = found_index

    def highlight_lyric_line(self, old_line_index, new_line_index):
        doc = self.lyrics_viewer.document()
        if old_line_index >= 0 and old_line_index < doc.blockCount():
            previous_block = doc.findBlockByNumber(old_line_index)
            cursor = QTextCursor(previous_block); cursor.select(QTextCursor.BlockUnderCursor); cursor.setCharFormat(self.normal_lyric_format)
        if new_line_index >= 0 and new_line_index < doc.blockCount():
            current_block = doc.findBlockByNumber(new_line_index)
            cursor = QTextCursor(current_block); cursor.select(QTextCursor.BlockUnderCursor); cursor.setCharFormat(self.highlighted_lyric_format)
            self.lyrics_viewer.setTextCursor(cursor); self.lyrics_viewer.ensureCursorVisible()

    # --- [SKIN BARU] Logika untuk Skin ---
    def change_skin(self, mode, force=False):
        """Mengganti skin/tata letak UI."""
        if not force and mode == self.current_skin:
            return
            
        self.previous_skin = self.current_skin
        self.current_skin = mode

        # Sembunyikan toolbar jika beralih dari mode toolbar
        if self.previous_skin == "toolbar" and self.toolbar_player:
            self.toolbar_player.hide()

        # Tampilkan jendela utama jika beralih ke mode selain toolbar
        if mode != "toolbar":
            self.show()

        # Update menu yang tercentang
        if mode == "normal": self.normal_skin_action.setChecked(True)
        elif mode == "compact": self.compact_skin_action.setChecked(True)
        elif mode == "minimal": self.minimal_skin_action.setChecked(True)
        elif mode == "toolbar": self.toolbar_skin_action.setChecked(True)
            
        self.apply_skin_layout()

    def apply_skin_layout(self):
        """Menerapkan perubahan UI berdasarkan skin yang aktif."""
        mode = self.current_skin

        # Sembunyikan panel playlist terlebih dahulu jika akan di-toggle
        self.right_panel_widget.hide()

        # Atur visibilitas komponen berdasarkan mode
        if mode == "normal":
            self.album_art_container_widget.show()
            self.artist_label.show()
            self.visualizer_widget.show()
            self.right_panel_widget.show()
            self.toggle_playlist_button.hide()
            self.maximize_button.show()

            self.setMinimumSize(self.skin_configs["normal"]["min_size"])
            self.setMaximumSize(16777215, 16777215)
            self.resize(self.sizeHint())

        elif mode == "compact":
            self.album_art_container_widget.hide()
            self.artist_label.show()
            self.visualizer_widget.show()
            self.toggle_playlist_button.show()
            self.maximize_button.hide()
            size = self.skin_configs["compact"]["size"]
            self.setFixedSize(size)

        elif mode == "minimal":
            self.album_art_container_widget.hide()
            self.artist_label.hide()
            self.visualizer_widget.hide()
            self.toggle_playlist_button.show()
            self.maximize_button.hide()
            size = self.skin_configs["minimal"]["size"]
            self.setFixedSize(size)

        elif mode == "toolbar":
            if not self.toolbar_player:
                self.toolbar_player = ToolbarPlayer(self)
                self.apply_current_visuals() # Terapkan style saat pertama kali dibuat
            
            self.toolbar_player.update_initial_state()
            self.toolbar_player.show()
            self.hide() # Sembunyikan jendela utama


    def toggle_playlist_visibility(self):
        """Menampilkan atau menyembunyikan panel playlist dalam mode compact/minimal."""
        if self.current_skin == "normal": return # Fungsi ini tidak berlaku di mode normal

        base_width = self.skin_configs[self.current_skin]["size"].width()

        if self.right_panel_widget.isVisible():
            self.right_panel_widget.hide()
            self.setFixedWidth(base_width)
        else:
            self.right_panel_widget.show()
            self.setFixedWidth(base_width + self.playlist_panel_width)

    def toggle_dynamic_aura(self, enabled):
        self.dynamic_aura_enabled = enabled
        if enabled and self.current_index != -1:
            path = self.playlist[self.current_index]
            metadata = self.get_track_metadata(path)
            artwork = metadata.get('artwork')
            self.current_dynamic_color = self.extract_dominant_color(artwork)
        else: self.current_dynamic_color = None
        self.apply_current_visuals()

    def extract_dominant_color(self, artwork_data):
        if not artwork_data: return None
        pixmap = QPixmap()
        if not pixmap.loadFromData(artwork_data): return None
        image = pixmap.toImage().scaled(1, 1, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        color = QColor(image.pixel(0, 0))
        if color.lightnessF() > 0.25 and color.lightnessF() < 0.8 and color.saturationF() > 0.3:
            return color.name()
        return None

    def change_theme(self, theme_id):
        self.current_theme = theme_id
        self.settings.setValue("theme", theme_id)
        self.apply_current_visuals()

    def apply_current_visuals(self):
        base_theme = THEMES.get(self.current_theme, THEMES["default"])
        if self.dynamic_aura_enabled and self.current_dynamic_color:
            dynamic_theme = base_theme.copy()
            dynamic_theme["accent"] = self.current_dynamic_color
            dynamic_theme["accent_hover"] = QColor(self.current_dynamic_color).darker(115).name()
            self.apply_stylesheet(dynamic_theme)
        else:
            self.apply_stylesheet(base_theme)

    def show_library_window(self):
        if self.library_window is None:
            theme = THEMES.get(self.current_theme, THEMES["default"])
            self.library_window = LibraryWindow(parent=self, initial_theme=theme)
            self.library_window.tracks_selected.connect(self.handle_library_selection)
        self.library_window.show()
        self.library_window.activateWindow()

    def show_radio_window(self):
        if self.radio_window is None:
            theme = THEMES.get(self.current_theme, THEMES["default"])
            self.radio_window = RadioWindow(parent=self, initial_theme=theme)
            self.radio_window.radio_playing.connect(self.pause_for_radio)
        self.radio_window.show()
        self.radio_window.activateWindow()

    def pause_for_radio(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play"]))
            self.visualizer_widget.stop()

    def handle_library_selection(self, data):
        paths = data.get('paths', []); action = data.get('action', 'play')
        if not paths: return
        if action == 'play': self.clear_playlist(); self.add_and_play_paths(paths)
        elif action == 'append':
            new_tracks = [p for p in paths if p not in self.playlist]
            if new_tracks:
                self.playlist.extend(new_tracks)
                self.regenerate_play_order(); self.update_playlist_display(); self.update_status_bar()
                QMessageBox.information(self, "Song Added", f"{len(new_tracks)} the song has been added to the queue.")

    def apply_stylesheet(self, theme):
        self.visualizer_widget.set_accent_color(theme["accent"])
        self.mini_player.apply_stylesheet(theme)
        if self.library_window: self.library_window.apply_stylesheet(theme)
        if self.radio_window: self.radio_window.apply_stylesheet(theme)
        if self.toolbar_player: self.toolbar_player.apply_stylesheet(theme) # [SKIN BARU]
        self.normal_lyric_format.setForeground(QColor(theme["text_primary"])); self.normal_lyric_format.setFontWeight(QFont.Normal)
        self.highlighted_lyric_format.setForeground(QColor(theme["accent"])); self.highlighted_lyric_format.setFontWeight(QFont.Bold)
        qss = f"""
            #container {{ background-color: {theme["bg_main"]}; border-radius: 12px; border: 1px solid {theme["border"]}; }}
            QWidget {{ color: {theme["text_primary"]}; font-family: Segoe UI, sans-serif; font-size: 14px; }}
            QMenu, QComboBox QAbstractItemView {{ background-color: {theme["bg_main"]}; border: 1px solid {theme["border"]}; }}
            QMenu::item:selected, QComboBox QAbstractItemView::item:selected {{ background-color: {theme["accent"]}; }}
            QComboBox {{ border: 1px solid {theme["border"]}; border-radius: 4px; padding: 4px; background-color: {theme["bg_secondary"]}; }}
            QComboBox::drop-down {{ border: none; }}
            #searchBar {{ background-color: {theme["bg_secondary"]}; border: 1px solid {theme["border"]}; border-radius: 6px; padding: 6px; }}
            #equalizerDialog, QDialog {{ background-color: {theme["bg_main"]}; }}
            #titleLabel {{ font-weight: bold; padding-left: 10px; color: {theme["text_secondary"]}; }}
            #albumArt {{ border: 1px solid {theme["border"]}; border-radius: 12px; background-color: {theme["bg_secondary"]}; }}
            #trackTitle {{ font-size: 20px; font-weight: bold; color: {theme["text_primary"]}; }}
            #artistLabel {{ font-size: 15px; color: {theme["text_secondary"]}; }}
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{ background-color: transparent; padding: 8px 15px; border-radius: 6px; color: {theme["text_secondary"]}; }}
            QTabBar::tab:hover {{ background-color: {theme["border"]}; }}
            QTabBar::tab:selected {{ background-color: {theme["accent"]}; color: #FFFFFF; }}
            #playlistWidget, #lyricsViewer {{ background-color: {theme["bg_secondary"]}; border: 1px solid {theme["border"]}; border-radius: 8px; padding: 5px; }}
            #playlistWidget::item {{ padding: 10px; border-radius: 5px; }}
            #playlistWidget::item:selected {{ background-color: {theme["accent"]}; color: #FFFFFF; }}
            #playlistWidget::item:hover:!selected {{ background-color: {theme["border"]}; }}
            #lyricsViewer {{ font-size: 16px; line-height: 150%; }}
            QSlider::groove:horizontal {{ border: 1px solid {theme["border"]}; height: 8px; background: {theme["bg_secondary"]}; margin: 2px 0; border-radius: 4px; }}
            QSlider::handle:horizontal {{ background: {theme["text_primary"]}; border: 1px solid {theme["text_primary"]}; width: 16px; margin: -4px 0; border-radius: 8px; }}
            QSlider::handle:horizontal:hover {{ background: {theme["accent"]}; border: 1px solid {theme["accent"]}; }}
            QSlider::sub-page:horizontal {{ background: {theme["accent"]}; border-radius: 4px; }}
            QSlider::groove:vertical {{ border: 1px solid {theme["border"]}; width: 8px; background: {theme["bg_secondary"]}; margin: 0 2px; border-radius: 4px; }}
            QSlider::handle:vertical {{ background: {theme["text_primary"]}; border: 1px solid {theme["text_primary"]}; height: 16px; margin: 0 -4px; border-radius: 8px; }}
            QSlider::handle:vertical:hover {{ background: {theme["accent"]}; border: 1px solid {theme["accent"]}; }}
            QSlider::sub-page:vertical {{ background: {theme["accent"]}; border-radius: 4px; }}
            QPushButton {{ border: none; background-color: transparent; }}
            #mainButton {{ background-color: {theme["accent"]}; color: #FFFFFF; border-radius: 30px; min-width: 60px; min-height: 60px; padding: 8px; }}
            #mainButton:hover {{ background-color: {theme["accent_hover"]}; }}
            #secondaryButton {{ background-color: transparent; border-radius: 24px; min-width: 48px; min-height: 48px; }}
            #iconButton, #windowControlButton {{ border-radius: 18px; min-width: 36px; min-height: 36px; }}
            #secondaryButton:hover, #iconButton:hover, #windowControlButton:hover {{ background-color: {theme["border"]}; }}
            #closeButton:hover {{ background-color: #E81123; }}
            #mainButton:pressed, #secondaryButton:pressed, #iconButton:pressed, #windowControlButton:pressed {{ background-color: #444; }}
            #secondaryButton[active="true"] {{ background-color: {theme["accent"]}; }}
            #secondaryButton[repeat_one="true"] {{ border: 1px solid {theme["accent"]}; }}
            QPushButton, QLabel {{ background-color: transparent; }}
            QStatusBar {{ color: {theme["text_secondary"]}; }}
            QStatusBar::item {{ border: none; }}
            QScrollBar:vertical {{ border: none; background: {theme["bg_secondary"]}; width: 10px; margin: 0px 0px 0px 0px; }}
            QScrollBar::handle:vertical {{ background: {theme["border"]}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::handle:vertical:hover {{ background: {theme["text_secondary"]}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """
        self.setStyleSheet(qss)
        text_color = theme["text_primary"]
        self.prev_button.setIcon(get_icon_from_svg(SVG_ICONS["previous"], color=text_color))
        self.next_button.setIcon(get_icon_from_svg(SVG_ICONS["next"], color=text_color))
        self.volume_button.setIcon(get_icon_from_svg(SVG_ICONS["volume-high" if self.volume_slider.value() > 0 else "volume-muted"], color=text_color))
        self.add_folder_button.setIcon(get_icon_from_svg(SVG_ICONS["add-folder"], color=text_color))
        self.clear_playlist_button.setIcon(get_icon_from_svg(SVG_ICONS["clear-playlist"], color=text_color))
        self.minimize_button.setIcon(get_icon_from_svg(SVG_ICONS["minimize"], color=text_color))
        self.shuffle_button.setIcon(get_icon_from_svg(SVG_ICONS["shuffle"], color=text_color))
        self.repeat_button.setIcon(get_icon_from_svg(SVG_ICONS["repeat"], color=text_color))
        self.tray_button.setIcon(get_icon_from_svg(SVG_ICONS["tray"], color=text_color))
        self.toggle_playlist_button.setIcon(get_icon_from_svg(SVG_ICONS["list"], color=text_color))
        is_maximized = self.isMaximized()
        self.maximize_button.setIcon(get_icon_from_svg(SVG_ICONS["restore" if is_maximized else "maximize"], color=text_color))
        self.close_button.setIcon(get_icon_from_svg(SVG_ICONS["close"], color=text_color))
        self.play_button.setIcon(get_icon_from_svg(SVG_ICONS["play" if self.player.state() != QMediaPlayer.PlayingState else "pause"]))
        self.update_shuffle_repeat_style()

if __name__ == '__main__':
    QApplication.setQuitOnLastWindowClosed(False)
    app = QApplication(sys.argv)

    if not MUTAGEN_AVAILABLE:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Pustaka 'mutagen' tidak ditemukan.")
        msg_box.setInformativeText("Fitur metadata tidak akan berfungsi.\nInstall dengan: pip install mutagen")
        msg_box.setWindowTitle("Peringatan")
        msg_box.exec_()

    player = AudioPlayer()

    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
        QTimer.singleShot(0, lambda: player.add_and_play_paths(file_paths))

    # Tampilkan jendela utama hanya jika skin default bukan toolbar
    saved_skin = player.settings.value("skin", "normal", type=str)
    if saved_skin != "toolbar":
        player.show()

    sys.exit(app.exec_())