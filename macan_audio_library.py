# macan_audio_library.py (Diperbarui dengan perbaikan clear & manajemen folder)

import sys
import os
import json
import time
from functools import partial

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QAbstractItemView, QHeaderView, QFileDialog, QMenu, QLineEdit,
    QInputDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QLabel, QTableWidgetItem,
    QDialog, QListWidget, QListWidgetItem  # [BARU] Impor tambahan untuk dialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QFileSystemWatcher, QSettings, QPoint
from PyQt5.QtGui import QColor

# Coba impor mutagen, jika gagal, fitur metadata akan terbatas
try:
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# [BARU] Jendela dialog untuk mengelola folder library
class ManageFoldersDialog(QDialog):
    def __init__(self, initial_folders, theme, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kelola Folder Library")
        self.setMinimumSize(500, 300)
        self.theme = theme

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        self.info_label = QLabel("Ini adalah daftar folder yang akan dipindai oleh library.")
        self.folder_list_widget = QListWidget()
        self.folder_list_widget.addItems(initial_folders)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Tambah Folder")
        self.remove_button = QPushButton("Hapus Folder Terpilih")
        self.close_button = QPushButton("Tutup")

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_button)

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.folder_list_widget)
        self.layout.addLayout(self.button_layout)

        self.add_button.clicked.connect(self.add_folder)
        self.remove_button.clicked.connect(self.remove_folder)
        self.close_button.clicked.connect(self.accept)
        
        self.apply_stylesheet()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Baru")
        if folder:
            # Cek apakah folder sudah ada di daftar
            items = [self.folder_list_widget.item(i).text() for i in range(self.folder_list_widget.count())]
            if folder not in items:
                self.folder_list_widget.addItem(folder)

    def remove_folder(self):
        selected_item = self.folder_list_widget.currentItem()
        if selected_item:
            self.folder_list_widget.takeItem(self.folder_list_widget.row(selected_item))

    def get_folders(self):
        return [self.folder_list_widget.item(i).text() for i in range(self.folder_list_widget.count())]

    def apply_stylesheet(self):
        if not self.theme: return
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme["bg_main"]};
                color: {self.theme["text_primary"]};
            }}
            QLabel {{
                color: {self.theme["text_secondary"]};
            }}
            QListWidget {{
                background-color: {self.theme["bg_secondary"]};
                border: 1px solid {self.theme["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {self.theme["accent"]};
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {self.theme["bg_secondary"]};
                border: 1px solid {self.theme["border"]};
                padding: 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.theme["border"]};
            }}
        """)


class LibraryWindow(QWidget):
    """
    Jendela Library musik yang terpisah.
    Mengelola pemindaian folder, menampilkan lagu, dan manajemen playlist.
    """
    tracks_selected = pyqtSignal(dict)

    def __init__(self, parent=None, initial_theme=None):
        super().__init__(parent)
        self.main_player = parent
        self.current_theme = initial_theme or {}
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_pos = QPoint()
        
        self.library = {}
        self.playlists = {"Saved": {}}
        
        self.watcher = QFileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.folder_changed)

        self.settings = QSettings("MacanCorp", "MacanAudioPlayerLibrary")

        self._init_ui()
        self.load_settings_and_data()
        self.apply_stylesheet(self.current_theme)

    def _init_ui(self):
        self.setWindowTitle("Macan Music Library")
        self.setGeometry(150, 150, 900, 700)
        
        self.main_container = QWidget()
        self.main_container.setObjectName("libraryContainer")
        
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(1, 1, 1, 1)
        container_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(15, 0, 5, 0)
        
        title_label = QLabel("Macan Music Library")
        title_label.setObjectName("titleLabel")
        
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(36, 36)
        self.close_button.clicked.connect(self.close)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.close_button)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 10, 15, 15)
        content_layout.setSpacing(15)

        left_panel = QVBoxLayout()
        self.playlist_tree = QTreeWidget()
        self.playlist_tree.setObjectName("playlistTree")
        self.playlist_tree.setHeaderHidden(True)
        self.playlist_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_tree.customContextMenuRequested.connect(self.show_playlist_context_menu)
        self.playlist_tree.itemClicked.connect(self.display_playlist_content)
        self.all_tracks_item = QTreeWidgetItem(self.playlist_tree, ["Semua Lagu"])
        self.smart_playlists_item = QTreeWidgetItem(self.playlist_tree, ["Smart Playlists"])
        self.saved_playlists_item = QTreeWidgetItem(self.playlist_tree, ["Saved Playlists"])
        self.recently_added_item = QTreeWidgetItem(self.smart_playlists_item, ["Baru Ditambahkan"])
        self.playlist_tree.expandAll()
        left_panel.addWidget(self.playlist_tree)

        right_panel = QVBoxLayout()
        toolbar_layout = QHBoxLayout()
        self.scan_button = QPushButton("Scan Folder Library")
        # [UBAH] Tombol diubah untuk memanggil dialog manajemen folder
        self.manage_folders_button = QPushButton("Kelola Folder Library")
        self.export_playlist_button = QPushButton("Export Playlist")
        self.clear_all_button = QPushButton("Clear All Library")
        self.clear_all_button.setObjectName("clearAllButton") 

        self.scan_button.clicked.connect(self.full_rescan)
        self.manage_folders_button.clicked.connect(self.manage_folders) # [UBAH] Koneksi diubah
        self.export_playlist_button.clicked.connect(self.export_selected_playlist)
        self.clear_all_button.clicked.connect(self.clear_all_library)

        toolbar_layout.addWidget(self.scan_button)
        toolbar_layout.addWidget(self.manage_folders_button) # [UBAH] Tombol diganti
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.clear_all_button)
        toolbar_layout.addWidget(self.export_playlist_button)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cari lagu dalam library...")
        self.search_bar.textChanged.connect(self.filter_table)

        self.track_table = QTableWidget()
        self.track_table.setObjectName("trackTable")
        self.track_table.setColumnCount(5)
        self.track_table.setHorizontalHeaderLabels(["Judul", "Artis", "Album", "Durasi", "Path"])
        self.track_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.track_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.track_table.verticalHeader().setVisible(False)
        self.track_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.track_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.track_table.setColumnHidden(4, True)
        self.track_table.itemDoubleClicked.connect(self.play_selected_track)
        self.track_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.track_table.customContextMenuRequested.connect(self.show_table_context_menu)
        self.track_table.setDragEnabled(True)
        self.track_table.setDragDropMode(QAbstractItemView.DragOnly)

        right_panel.addLayout(toolbar_layout)
        right_panel.addWidget(self.search_bar)
        right_panel.addWidget(self.track_table)
        
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)

        container_layout.addWidget(self.title_bar)
        container_layout.addLayout(content_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.title_bar.rect().contains(event.pos() - self.main_container.pos()):
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = QPoint()
        event.accept()
    
    def load_settings_and_data(self):
        """Memuat folder scan, library, dan playlist dari QSettings dan file JSON."""
        self.scan_folders = self.settings.value("scan_folders", [], type=list)
        if self.scan_folders:
            self.watcher.addPaths(self.scan_folders)
            
        # Muat library dari file JSON
        library_path = self.settings.value("library_path", "")
        if library_path and os.path.exists(library_path):
            try:
                with open(library_path, 'r', encoding='utf-8') as f:
                    self.library = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.library = {}
        
        # Muat playlists dari file JSON
        playlists_path = self.settings.value("playlists_path", "")
        if playlists_path and os.path.exists(playlists_path):
            try:
                with open(playlists_path, 'r', encoding='utf-8') as f:
                    self.playlists = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.playlists = {"Saved": {}}

        # Pastikan struktur dasar playlist ada
        if "Saved" not in self.playlists:
            self.playlists["Saved"] = {}
            
        self.update_playlist_tree()
        self.populate_table(list(self.library.keys()))

    def save_data(self):
        """Menyimpan library dan playlist ke file JSON di folder data aplikasi."""
        # Tentukan path penyimpanan di folder data aplikasi
        app_data_path = os.path.dirname(self.settings.fileName())
        
        # Buat direktori jika belum ada
        if not os.path.exists(app_data_path):
            try:
                os.makedirs(app_data_path)
            except OSError as e:
                print(f"Error creating directory {app_data_path}: {e}")
                return

        # Simpan library
        library_path = os.path.join(app_data_path, "library.json")
        try:
            with open(library_path, 'w', encoding='utf-8') as f:
                json.dump(self.library, f, indent=4)
            self.settings.setValue("library_path", library_path)
            print(f"Library saved to: {library_path}")
        except IOError as e:
            print(f"Error saat menyimpan file library: {e}")
            
        # Simpan playlist
        playlists_path = os.path.join(app_data_path, "playlists.json")
        try:
            with open(playlists_path, 'w', encoding='utf-8') as f:
                json.dump(self.playlists, f, indent=4)
            self.settings.setValue("playlists_path", playlists_path)
            print(f"Playlists saved to: {playlists_path}")
        except IOError as e:
            print(f"Error saat menyimpan file playlist: {e}")
            
    def closeEvent(self, event):
        self.save_data()
        super().closeEvent(event)

    # [BARU] Fungsi untuk membuka dialog manajemen folder
    def manage_folders(self):
        dialog = ManageFoldersDialog(self.scan_folders, self.current_theme, self)
        if dialog.exec_() == QDialog.Accepted:
            new_folders = dialog.get_folders()
            if new_folders != self.scan_folders:
                # Hentikan pemantauan folder lama
                if self.scan_folders:
                    self.watcher.removePaths(self.scan_folders)
                
                # Perbarui dan simpan daftar folder baru
                self.scan_folders = new_folders
                self.settings.setValue("scan_folders", self.scan_folders)
                
                # Mulai pemantauan folder baru
                if self.scan_folders:
                    self.watcher.addPaths(self.scan_folders)
                
                QMessageBox.information(self, "Daftar Folder Diperbarui",
                                        "Daftar folder telah diperbarui.\n"
                                        "Jalankan 'Scan Folder Library' untuk menerapkan perubahan.")

    def full_rescan(self):
        if not self.scan_folders:
            QMessageBox.warning(self, "Tidak Ada Folder", "Silakan tambahkan folder ke library terlebih dahulu melalui 'Kelola Folder Library'.")
            return
        supported_formats = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".mp4")
        current_tracks = set()
        for folder in self.scan_folders:
            for root, _, files in os.walk(folder):
                for filename in files:
                    if filename.lower().endswith(supported_formats):
                        path = os.path.join(root, filename)
                        current_tracks.add(path)
                        if path not in self.library:
                            self.library[path] = self._get_metadata(path)
        removed_tracks = set(self.library.keys()) - current_tracks
        for path in removed_tracks: del self.library[path]
        for pl_name, pl_tracks in self.playlists["Saved"].items():
            self.playlists["Saved"][pl_name] = [track for track in pl_tracks if track not in removed_tracks]
        self.populate_table(list(self.library.keys()))
        self.update_playlist_tree()
        QMessageBox.information(self, "Scan Selesai", f"Library diperbarui. Total {len(self.library)} lagu.")

    def folder_changed(self, path):
        print(f"Perubahan terdeteksi di: {path}. Menjadwalkan pemindaian ulang...")
        self.full_rescan()

    def _get_metadata(self, path):
        metadata = {'title': os.path.basename(path), 'artist': 'Unknown', 'album': 'Unknown', 'duration': 'N/A', 'added_date': time.time()}
        if not MUTAGEN_AVAILABLE: return metadata
        try:
            audio = None
            if path.lower().endswith('.mp3'): audio = MP3(path)
            elif path.lower().endswith('.flac'): audio = FLAC(path)
            elif path.lower().endswith(('.m4a', '.mp4')): audio = MP4(path)
            if audio:
                if path.lower().endswith('.mp3'):
                    metadata['title'] = str(audio.get('TIT2', [metadata['title']])[0])
                    metadata['artist'] = str(audio.get('TPE1', [metadata['artist']])[0])
                    metadata['album'] = str(audio.get('TALB', [metadata['album']])[0])
                elif path.lower().endswith('.flac'):
                    metadata['title'] = audio.get('title', [metadata['title']])[0]
                    metadata['artist'] = audio.get('artist', [metadata['artist']])[0]
                    metadata['album'] = audio.get('album', [metadata['album']])[0]
                elif path.lower().endswith(('.m4a', '.mp4')):
                    tags = audio.tags
                    if tags:
                        metadata['title'] = tags.get('\xa9nam', [metadata['title']])[0]
                        metadata['artist'] = tags.get('\xa9ART', [metadata['artist']])[0]
                        metadata['album'] = tags.get('\xa9alb', [metadata['album']])[0]
                duration_sec = int(audio.info.length)
                minutes, seconds = divmod(duration_sec, 60)
                metadata['duration'] = f"{minutes}:{seconds:02}"
        except Exception as e: print(f"Error reading metadata for {path}: {e}")
        return metadata

    def populate_table(self, track_paths):
        self.track_table.setRowCount(0)
        valid_paths = set(track_paths)
        for path in valid_paths:
            if path in self.library:
                metadata = self.library[path]
                row_position = self.track_table.rowCount()
                self.track_table.insertRow(row_position)
                self.track_table.setItem(row_position, 0, QTableWidgetItem(metadata['title']))
                self.track_table.setItem(row_position, 1, QTableWidgetItem(metadata['artist']))
                self.track_table.setItem(row_position, 2, QTableWidgetItem(metadata['album']))
                self.track_table.setItem(row_position, 3, QTableWidgetItem(metadata['duration']))
                self.track_table.setItem(row_position, 4, QTableWidgetItem(path))
        self.track_table.sortItems(0, Qt.AscendingOrder)
        self.search_bar.setText("")

    def filter_table(self, text):
        query = text.lower()
        for i in range(self.track_table.rowCount()):
            title = self.track_table.item(i, 0).text().lower()
            artist = self.track_table.item(i, 1).text().lower()
            album = self.track_table.item(i, 2).text().lower()
            if query in title or query in artist or query in album: self.track_table.setRowHidden(i, False)
            else: self.track_table.setRowHidden(i, True)

    def play_selected_track(self, item):
        path = self.track_table.item(item.row(), 4).text()
        self.tracks_selected.emit({'paths': [path], 'action': 'play'})

    def get_selected_track_paths(self):
        paths = []
        selected_rows = sorted(list(set(index.row() for index in self.track_table.selectedIndexes())))
        for row in selected_rows: paths.append(self.track_table.item(row, 4).text())
        return paths

    def update_playlist_tree(self):
        self.saved_playlists_item.takeChildren()
        if "Saved" not in self.playlists: self.playlists["Saved"] = {}
        for name in sorted(self.playlists["Saved"].keys()):
            count = len(self.playlists["Saved"][name])
            QTreeWidgetItem(self.saved_playlists_item, [f"{name} ({count})"])
        self.all_tracks_item.setText(0, f"Semua Lagu ({len(self.library)})")

    def display_playlist_content(self, item, column):
        if not item:
            return

        if item == self.all_tracks_item:
            self.populate_table(list(self.library.keys()))
        elif item.parent() == self.saved_playlists_item:
            playlist_name = item.text(0).split(' (')[0]
            if playlist_name in self.playlists["Saved"]:
                self.populate_table(self.playlists["Saved"][playlist_name])
        elif item == self.recently_added_item:
            sorted_tracks = sorted(self.library.items(), key=lambda x: x[1]['added_date'], reverse=True)
            recent_paths = [path for path, meta in sorted_tracks[:50]]
            self.populate_table(recent_paths)

    def create_new_playlist(self):
        name, ok = QInputDialog.getText(self, "Playlist Baru", "Masukkan nama playlist:")
        if ok and name:
            if name not in self.playlists["Saved"]:
                self.playlists["Saved"][name] = []
                self.update_playlist_tree()
            else: QMessageBox.warning(self, "Nama Sudah Ada", "Playlist dengan nama tersebut sudah ada.")
    
    def save_selection_as_playlist(self):
        """Membuat playlist baru dari lagu-lagu yang dipilih di tabel."""
        paths_to_save = self.get_selected_track_paths()
        if not paths_to_save:
            QMessageBox.information(self, "Tidak Ada Lagu Terpilih", "Silakan pilih satu atau beberapa lagu dari tabel terlebih dahulu.")
            return

        name, ok = QInputDialog.getText(self, "Playlist Baru", "Masukkan nama untuk playlist baru:")
        if ok and name:
            if name not in self.playlists["Saved"]:
                self.playlists["Saved"][name] = paths_to_save
                self.update_playlist_tree()
                QMessageBox.information(self, "Playlist Dibuat", f"Playlist '{name}' berhasil dibuat dengan {len(paths_to_save)} lagu.")
            else:
                QMessageBox.warning(self, "Nama Sudah Ada", "Playlist dengan nama tersebut sudah ada. Silakan gunakan nama lain.")

    def add_tracks_to_playlist(self, playlist_name):
        paths_to_add = self.get_selected_track_paths()
        if not paths_to_add:
            QMessageBox.information(self, "Tidak Ada Lagu", "Pilih lagu terlebih dahulu untuk ditambahkan.")
            return
        playlist = self.playlists["Saved"].get(playlist_name, [])
        added_count = 0
        for path in paths_to_add:
            if path not in playlist:
                playlist.append(path)
                added_count += 1
        self.playlists["Saved"][playlist_name] = playlist
        self.update_playlist_tree()
        QMessageBox.information(self, "Lagu Ditambahkan", f"{added_count} lagu baru ditambahkan ke playlist '{playlist_name}'.")

    def remove_playlist(self, playlist_name):
        if playlist_name in self.playlists["Saved"]:
            reply = QMessageBox.question(self, "Hapus Playlist", f"Anda yakin ingin menghapus playlist '{playlist_name}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.playlists["Saved"][playlist_name]
                self.update_playlist_tree()
                self.playlist_tree.setCurrentItem(self.all_tracks_item)
                self.display_playlist_content(self.all_tracks_item, 0)

    def remove_tracks_from_library(self):
        paths_to_remove = self.get_selected_track_paths()
        if not paths_to_remove: return
        
        reply = QMessageBox.question(self, "Hapus dari Library", 
            f"Anda yakin ingin menghapus {len(paths_to_remove)} lagu secara permanen dari library?\n(File tidak akan dihapus dari komputer)",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for path in paths_to_remove:
                if path in self.library:
                    del self.library[path]
                for name in self.playlists["Saved"]:
                    if path in self.playlists["Saved"][name]:
                        self.playlists["Saved"][name].remove(path)
            
            self.display_playlist_content(self.playlist_tree.currentItem(), 0)
            self.update_playlist_tree()

    def remove_tracks_from_current_playlist(self, playlist_name):
        paths_to_remove = self.get_selected_track_paths()
        if not paths_to_remove: return

        if playlist_name in self.playlists["Saved"]:
            for path in paths_to_remove:
                if path in self.playlists["Saved"][playlist_name]:
                    self.playlists["Saved"][playlist_name].remove(path)
            
            self.populate_table(self.playlists["Saved"][playlist_name])
            self.update_playlist_tree()

    def clear_playlist(self, playlist_name):
        if playlist_name in self.playlists["Saved"]:
            reply = QMessageBox.question(self, "Kosongkan Playlist", 
                f"Anda yakin ingin menghapus semua lagu dari playlist '{playlist_name}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.playlists["Saved"][playlist_name] = []
                current_item = self.playlist_tree.currentItem()
                if current_item:
                    current_item_text = current_item.text(0).split(' (')[0]
                    if current_item_text == playlist_name:
                        self.populate_table([])
                self.update_playlist_tree()

    # [FIX] Fungsi clear_all_library diperbaiki
    def clear_all_library(self):
        """Menghapus semua lagu, playlist, dan daftar folder dari library."""
        reply = QMessageBox.question(self, "Bersihkan Seluruh Library", 
            "PERINGATAN: Aksi ini akan menghapus SEMUA lagu, playlist, dan daftar folder pemindaian dari library.\n\nAnda yakin ingin melanjutkan?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Hentikan pemantauan folder
            if self.scan_folders:
                self.watcher.removePaths(self.scan_folders)
            
            # Hapus data dari memori
            self.library = {}
            self.playlists = {"Saved": {}}
            self.scan_folders = []
            
            # Hapus data dari penyimpanan (QSettings)
            self.settings.setValue("scan_folders", [])
            self.settings.remove("library_path")
            self.settings.remove("playlists_path")
            
            # Perbarui UI
            self.populate_table([])
            self.update_playlist_tree()
            QMessageBox.information(self, "Library Dibersihkan", "Semua lagu, playlist, dan daftar folder telah dihapus.")

    def export_selected_playlist(self):
        current_item = self.playlist_tree.currentItem()
        if not current_item or current_item.parent() != self.saved_playlists_item:
            QMessageBox.warning(self, "Pilih Playlist", "Pilih 'Saved Playlist' terlebih dahulu untuk diekspor.")
            return
        playlist_name = current_item.text(0).split(' (')[0]
        paths = self.playlists["Saved"].get(playlist_name)
        if not paths:
            QMessageBox.warning(self, "Playlist Kosong", "Playlist ini tidak berisi lagu.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Playlist", f"{playlist_name}.m3u", "M3U Playlist (*.m3u)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("#EXTM3U\n")
                    for path in paths: f.write(path + "\n")
                QMessageBox.information(self, "Ekspor Berhasil", f"Playlist '{playlist_name}' berhasil diekspor.")
            except Exception as e: QMessageBox.critical(self, "Error", f"Gagal mengekspor playlist: {e}")

    def show_table_context_menu(self, position):
        menu = QMenu(self)
        play_action = menu.addAction("Putar di Player Utama")
        append_action = menu.addAction("Tambahkan ke Antrian Player")
        menu.addSeparator()
        
        add_to_playlist_menu = menu.addMenu("Tambahkan ke Playlist")
        if not self.playlists["Saved"]:
            add_to_playlist_menu.addAction("Tidak ada playlist").setEnabled(False)
        else:
            for name in sorted(self.playlists["Saved"].keys()):
                action = add_to_playlist_menu.addAction(name)
                action.triggered.connect(partial(self.add_tracks_to_playlist, name))
        
        save_as_playlist_action = menu.addAction("Simpan Pilihan sebagai Playlist Baru")
        save_as_playlist_action.triggered.connect(self.save_selection_as_playlist)
        
        menu.addSeparator()
        current_playlist_item = self.playlist_tree.currentItem()
        is_saved_playlist_view = current_playlist_item and current_playlist_item.parent() == self.saved_playlists_item
        
        if is_saved_playlist_view:
            pl_name = current_playlist_item.text(0).split(' (')[0]
            remove_from_pl_action = menu.addAction(f"Hapus dari Playlist '{pl_name}'")
            remove_from_pl_action.triggered.connect(lambda: self.remove_tracks_from_current_playlist(pl_name))
        
        remove_from_lib_action = menu.addAction("Hapus dari Library")
        remove_from_lib_action.triggered.connect(self.remove_tracks_from_library)
        
        action = menu.exec_(self.track_table.mapToGlobal(position))
        if action == play_action:
            paths = self.get_selected_track_paths()
            if paths: self.tracks_selected.emit({'paths': paths, 'action': 'play'})
        elif action == append_action:
            paths = self.get_selected_track_paths()
            if paths: self.tracks_selected.emit({'paths': paths, 'action': 'append'})

    def show_playlist_context_menu(self, position):
        item = self.playlist_tree.itemAt(position)
        if not item: return
        menu = QMenu(self)
        
        if item == self.saved_playlists_item or item.parent() == self.saved_playlists_item:
            new_action = menu.addAction("Buat Playlist Baru")
            new_action.triggered.connect(self.create_new_playlist)
        
        if item.parent() == self.saved_playlists_item:
            playlist_name = item.text(0).split(' (')[0]
            menu.addSeparator()
            clear_action = menu.addAction("Kosongkan Playlist")
            clear_action.triggered.connect(partial(self.clear_playlist, playlist_name))
            delete_action = menu.addAction("Hapus Playlist Ini")
            delete_action.triggered.connect(partial(self.remove_playlist, playlist_name))

        if menu.actions():
            menu.exec_(self.playlist_tree.mapToGlobal(position))

    def apply_stylesheet(self, theme):
        if not theme: return
        self.current_theme = theme
        
        qss = f"""
            #libraryContainer {{
                background-color: {theme["bg_main"]};
                color: {theme["text_primary"]};
                border: 1px solid {theme["border"]};
                border-radius: 12px;
            }}
            #titleBar {{
                background-color: {theme["bg_secondary"]};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            #titleLabel {{
                font-weight: bold;
                color: {theme["text_secondary"]};
            }}
            #closeButton {{
                background-color: transparent;
                border: none;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }}
            #closeButton:hover {{
                background-color: #E81123;
                color: white;
            }}
            QPushButton {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                padding: 8px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme["border"]};
            }}
            #clearAllButton {{
                color: #FFFFFF;
                background-color: #c94444;
                border-color: #a33333;
            }}
            #clearAllButton:hover {{
                background-color: #E81123;
            }}
            QLineEdit, QTableWidget, QTreeWidget {{
                background-color: {theme["bg_secondary"]};
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {theme["bg_main"]};
                border: 1px solid {theme["border"]};
                padding: 4px;
            }}
            QTableWidget::item:selected, QTreeWidget::item:selected {{
                background-color: {theme["accent"]};
                color: #FFFFFF;
            }}
            QTableWidget::item:hover:!selected, QTreeWidget::item:hover:!selected {{
                background-color: {theme["border"]};
            }}
            QMenu {{
                background-color: {theme["bg_main"]};
                border: 1px solid {theme["border"]};
            }}
            QMenu::item:selected {{
                background-color: {theme["accent"]};
            }}
        """
        self.setStyleSheet(qss)