from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QComboBox, QMenuBar, QMenu, QTreeWidgetItemIterator, QDialog, QProgressBar, QSizePolicy, QLineEdit, QSlider
from PySide6.QtGui import QPixmap, QAction, QShortcut, QKeySequence, QFont, QTextCursor, QTextCharFormat, QColor
from PySide6.QtCore import Qt, QTimer, QThread, QEvent, QPropertyAnimation, QEasingCurve
from tagqt.ui.theme import Theme
from tagqt.ui.tracks import FileList
from tagqt.ui.side import Sidebar
from tagqt.core.tags import MetadataHandler
from tagqt.core.lyric import LyricsFetcher
from tagqt.core.roman import Romanizer
from tagqt.core.art import CoverArtManager
from tagqt.core.case import CaseConverter
from tagqt.core.rename import Renamer
from tagqt.core.flac import FlacEncoder, DependencyChecker
from tagqt.core.musicbrainz import MusicBrainzClient
from tagqt.core.settings import Settings
from tagqt.ui import dialogs
from tagqt.ui.batch_status import ClickableProgressBar, BatchStatusDialog, ClickableLabel
from tagqt.ui.workers import (
    LyricsWorker, AutoTagWorker, FolderLoaderWorker, RenameWorker,
    CoverFetchWorker, CoverResizeWorker, RomanizeWorker, CaseConvertWorker,
    FlacReencodeWorker, CsvImportWorker, SaveWorker
)
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QApplication
        self.setWindowIcon(QApplication.instance().windowIcon())
        from tagqt.version import __version__
        self.setWindowTitle(f"TagQt {__version__}")
        self.resize(1200, 800)
        
        # Core Logic
        self.metadata = None
        self.current_file = None
        self.lyrics_fetcher = LyricsFetcher()
        self.romanizer = Romanizer()
        self.cover_manager = CoverArtManager()
        self.settings = Settings()
        
        # Batch State
        self.batch_dialog = None
        self.batch_running = False
        self._status_is_batch = False
        self._persistent_toast = None # (message, is_batch)
        self.thread = None
        self.worker = None

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (Vertical to include header)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Menu Bar
        self.create_menu_bar()
        
        # Keyboard Shortcuts
        self.setup_shortcuts()
        
        # Header / Toolbar
        header_layout = QHBoxLayout()
        
        import os
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtGui import QPixmap, QPainter
        self.title_label = QLabel()
        import sys
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, 'assets', 'logo.svg')
        else:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'logo.svg')
        renderer = QSvgRenderer(logo_path)
        svg_size = renderer.defaultSize()
        target_h = 32
        target_w = int(svg_size.width() * target_h / svg_size.height())
        logo_pixmap = QPixmap(target_w, target_h)
        logo_pixmap.fill(Qt.transparent)
        painter = QPainter(logo_pixmap)
        renderer.render(painter)
        painter.end()
        self.title_label.setPixmap(logo_pixmap)
        self.title_label.setStyleSheet("background: transparent;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Notification Area (Right Aligned)
        self.notification_layout = QHBoxLayout()
        self.notification_layout.setSpacing(15)
        
        # Selection Debounce Timer
        self.selection_timer = QTimer(self)
        self.selection_timer.setSingleShot(True)
        self.selection_timer.timeout.connect(self._handle_selection_deferred)
        
        # Initialize Toast Manager
        from tagqt.ui.toast import ToastManager
        self.toast_manager = ToastManager(self)
        
        # Cancel Button (Left of Progress)
        self.batch_cancel_btn = QPushButton("Cancel")
        self.batch_cancel_btn.setVisible(False)
        self.batch_cancel_btn.setCursor(Qt.PointingHandCursor)
        self.batch_cancel_btn.clicked.connect(self.cancel_batch_operation)
        self.batch_cancel_btn.setFixedWidth(70)
        self.batch_cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
                font-size: 11px;
                font-weight: 600;
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 4px 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.RED};
                color: {Theme.TOAST_TEXT};
                border: 1px solid {Theme.RED};
            }}
            QPushButton:pressed {{
                background-color: {Theme.ACCENT_DIM};
            }}
            QPushButton:disabled {{
                background-color: {Theme.SURFACE2};
                color: {Theme.SUBTEXT0};
            }}
        """)
        self.notification_layout.addWidget(self.batch_cancel_btn, 0, Qt.AlignVCenter)
        
        # Batch Progress Area
        self.batch_container = QWidget()
        self.batch_container.setVisible(False)
        self.batch_container.setFixedWidth(300) # Increased width
        batch_layout = QVBoxLayout(self.batch_container)
        batch_layout.setContentsMargins(0, 0, 0, 0)
        batch_layout.setSpacing(0)
        
        # Clickable Frame for Progress
        self.progress_frame = QWidget()
        self.progress_frame.setCursor(Qt.PointingHandCursor)
        self.progress_frame.mousePressEvent = self.on_progress_click
        self.progress_frame.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 6px;
                border: none;
            }}
            QWidget:hover {{
                background-color: {Theme.SURFACE0};
            }}
        """)
        
        frame_layout = QVBoxLayout(self.progress_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(4)
        
        # Progress Label (status text shown above bar)
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.SUBTEXT1};
                font-size: 12px;
                font-weight: normal;
                background: transparent;
                border: none;
            }}
        """)
        self.progress_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        frame_layout.addWidget(self.progress_label)
        
        # Progress Bar (slim, no text inside)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {Theme.SURFACE0};
                border-radius: 3px;
                min-height: 6px;
                max-height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 3px;
            }}
        """)
        frame_layout.addWidget(self.progress_bar)
        
        self._progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self._progress_animation.setDuration(150)
        self._progress_animation.setEasingCurve(QEasingCurve.OutCubic)

        batch_layout.addWidget(self.progress_frame)
        
        self.notification_layout.addWidget(self.batch_container)
        
        header_layout.addLayout(self.notification_layout)
        
        main_layout.addLayout(header_layout)

        # Content Layout (Horizontal)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left Panel (File List + Filter)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Filter Input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by name, title, artist, album...")
        self.filter_input.setClearButtonEnabled(True)
        self.filter_input.textChanged.connect(self.on_filter_changed)
        self.filter_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.SURFACE0};
                border: 1px solid {Theme.SURFACE1};
                border-radius: {Theme.CORNER_RADIUS};
                padding: 10px 15px;
                color: {Theme.TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.ACCENT};
            }}
        """)
        left_panel.addWidget(self.filter_input)
        
        # Filter Debounce Timer
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(200)
        self.filter_timer.timeout.connect(self._apply_filter)
        
        # File List (Left/Center)
        self.file_list = FileList()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.files_dropped.connect(self.on_files_dropped)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.file_list.itemDoubleClicked.connect(self._on_tree_double_click)
        left_panel.addWidget(self.file_list)
        
        content_layout.addLayout(left_panel, stretch=2)
        
        # Sidebar (Right)
        self.sidebar = Sidebar()
        self.sidebar.save_clicked.connect(self.save_metadata)
        self.sidebar.romanize_clicked.connect(self.romanize_metadata)
        self.sidebar.lyrics_clicked.connect(self.fetch_lyrics)
        self.sidebar.cover_clicked.connect(self.search_cover)
        self.sidebar.load_cover_clicked.connect(self.load_cover_from_file)
        self.sidebar.load_lyrics_clicked.connect(self.load_lyrics_from_file)
        self.sidebar.cancel_global_clicked.connect(self.exit_global_mode)
        self.sidebar.reencode_flac_clicked.connect(self.reencode_flac_selected)
        content_layout.addWidget(self.sidebar, stretch=1)
        
        main_layout.addLayout(content_layout)
        
        # ── Player Bar ──────────────────────────────────────────────────
        from tagqt.ui.player import PlayerController
        self.player = PlayerController(self)
        self.player.state_changed.connect(self._on_player_state_changed)
        self.player.track_changed.connect(self._on_player_track_changed)
        self.player.position_changed.connect(self._on_player_position_changed)
        self.player.lyric_line_changed.connect(self._on_lyric_line_changed)
        self._now_playing_item = None  # track the bolded row
        self._lyrics_sync_paused = False
        
        player_bar = QWidget()
        player_bar.setStyleSheet(f"""
            QWidget#playerBar {{
                background-color: {Theme.CRUST};
                border-top: 1px solid {Theme.SURFACE1};
            }}
        """)
        player_bar.setObjectName("playerBar")
        player_bar_layout = QHBoxLayout(player_bar)
        player_bar_layout.setContentsMargins(16, 8, 16, 8)
        player_bar_layout.setSpacing(10)
        
        # Transport buttons
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT};
                border: none;
                font-size: 16px;
                padding: 4px 8px;
                min-height: 22px;
                min-width: 28px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE0};
                border-radius: 4px;
            }}
            QPushButton:pressed {{
                background-color: {Theme.SURFACE1};
            }}
        """
        
        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setStyleSheet(btn_style)
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.setToolTip("Previous track")
        self.btn_prev.clicked.connect(self.player.prev_track)
        player_bar_layout.addWidget(self.btn_prev)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setStyleSheet(btn_style)
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setToolTip("Play / Pause")
        self.btn_play.clicked.connect(self._on_play_btn_clicked)
        player_bar_layout.addWidget(self.btn_play)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setStyleSheet(btn_style)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.clicked.connect(self.player.stop)
        player_bar_layout.addWidget(self.btn_stop)
        
        self.btn_next = QPushButton("⏭")
        self.btn_next.setStyleSheet(btn_style)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setToolTip("Next track")
        self.btn_next.clicked.connect(self.player.next_track)
        player_bar_layout.addWidget(self.btn_next)
        
        # Seek slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.player.seek)
        player_bar_layout.addWidget(self.seek_slider, stretch=1)
        
        # Time label
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.SUBTEXT0};
                font-size: 11px;
                background: transparent;
                border: none;
                min-width: 80px;
            }}
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        player_bar_layout.addWidget(self.time_label)
        
        # Volume slider
        vol_label = QLabel("🔊")
        vol_label.setStyleSheet(f"color: {Theme.SUBTEXT0}; font-size: 13px; background: transparent; border: none;")
        player_bar_layout.addWidget(vol_label)
        self._vol_label = vol_label  # store for theme refresh
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(lambda v: self.player.set_volume(v / 100.0))
        player_bar_layout.addWidget(self.volume_slider)
        
        # Now-playing label
        self.now_playing_label = QLabel("")
        self.now_playing_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.SUBTEXT1};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
        """)
        self.now_playing_label.setMinimumWidth(120)
        self.now_playing_label.setMaximumWidth(300)
        player_bar_layout.addWidget(self.now_playing_label)
        
        self.player_bar_widget = player_bar  # store for theme refresh
        main_layout.addWidget(player_bar)
        
        # Install event filter on sidebar to pause lyrics sync when user edits
        self.sidebar.installEventFilter(self)
        
        # Load saved theme
        if self.settings.get_light_theme():
            Theme.set_light_mode(True)
            self.theme_action.setChecked(True)
        
        # Apply Theme
        self.setStyleSheet(Theme.get_stylesheet())

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_metadata)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_folder_dialog)
        QShortcut(QKeySequence("Escape"), self, self.exit_global_mode)
        QShortcut(QKeySequence("Ctrl+K"), self, self.show_command_palette)
        
        from tagqt.ui.palette import CommandPalette
        self.command_palette = CommandPalette(self)
        self.command_palette.register_commands([
            {"name": "Open folder", "shortcut": "Ctrl+O", "callback": self.open_folder_dialog},
            {"name": "Save changes", "shortcut": "Ctrl+S", "callback": self.save_metadata},
            {"name": "Fetch covers (all)", "shortcut": "", "callback": self.fetch_all_covers},
            {"name": "Fetch lyrics (all)", "shortcut": "", "callback": self.fetch_all_lyrics},
            {"name": "Rename files", "shortcut": "", "callback": self.rename_all_files},
            {"name": "Auto-tag (all)", "shortcut": "", "callback": self.autotag_all},
            {"name": "Re-encode FLAC", "shortcut": "", "callback": self.reencode_flac_selected},
            {"name": "Romanize lyrics", "shortcut": "", "callback": self.romanize_all},
            {"name": "Resize covers", "shortcut": "", "callback": self.resize_all_covers},
            {"name": "Toggle theme", "shortcut": "", "callback": lambda: self.toggle_theme(not Theme._is_light)},
            {"name": "Exit global edit", "shortcut": "Escape", "callback": self.exit_global_mode},
            {"name": "Hints and tips", "shortcut": "", "callback": self.show_hints},
            {"name": "About TagQt", "shortcut": "", "callback": self.show_about},
        ])

    def show_command_palette(self):
        self.command_palette.show()

    def closeEvent(self, event):
        """Warn about unsaved changes and clean up threads before closing."""
        # Stop player on close
        if hasattr(self, 'player'):
            self.player.stop()
        
        # Check for unsaved changes in single-file mode
        has_unsaved = False
        if self.metadata and not getattr(self.sidebar, 'is_global_mode', False):
            # Compare current sidebar values to loaded metadata
            if (self.sidebar.title_edit.text() != (self.metadata.title or '') or
                self.sidebar.artist_edit.text() != (self.metadata.artist or '') or
                self.sidebar.album_edit.text() != (self.metadata.album or '')):
                has_unsaved = True
        
        if has_unsaved:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Unsaved Changes")
            msg.setText("You have unsaved changes.")
            msg.setInformativeText("Save before closing?")
            save_btn = msg.addButton("Save and quit", QMessageBox.AcceptRole)
            discard_btn = msg.addButton("Discard", QMessageBox.DestructiveRole)
            cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
            msg.setDefaultButton(save_btn)
            msg.exec()
            
            if msg.clickedButton() == save_btn:
                self.save_metadata()
            elif msg.clickedButton() == cancel_btn:
                event.ignore()
                return
            # Discard: fall through to close
        
        if self.batch_running:
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Task Running",
                "A background task is still running. Quit anyway?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        try:
            if self.batch_running and hasattr(self, 'worker') and self.worker:
                self.worker.stop()
            if hasattr(self, 'thread') and self.thread:
                try:
                    if self.thread.isRunning():
                        self.thread.quit()
                        self.thread.wait(2000)
                except RuntimeError:
                    pass
        except Exception:
            pass
        event.accept()
        super().closeEvent(event)

    def on_progress_click(self, event):
        self.show_batch_details()

    def show_toast(self, message, duration=3000, is_batch=False):
        # Use new ToastManager
        # If is_batch is True, it might be a persistent status update?
        # The user said "move new toast to another place".
        # We'll use the overlay for all toasts.
        self.toast_manager.show_message(message, duration)
    

    def _prepare_batch(self, title):
        if self.batch_running:
            # Check if thread is actually running
            is_running = False
            if self.thread:
                try:
                    is_running = self.thread.isRunning()
                except RuntimeError:
                    # C++ object already deleted
                    self.thread = None
                    self.worker = None
            
            if is_running:
                dialogs.show_warning(self, "Busy", "Another task is still running. Wait for it to finish or cancel it first.")
                return False
            else:
                # Stale state, reset
                self.batch_running = False
            
        if not self.batch_dialog:
            self.batch_dialog = BatchStatusDialog(self, title)
        else:
            self.batch_dialog.setWindowTitle(title)
            self.batch_dialog.clear()
            
        self.batch_running = True
        self._status_is_batch = True
        self._persistent_toast = None
        # self.toast_label.setVisible(False) # Removed
        self.batch_container.setVisible(True)
        self.batch_cancel_btn.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting…")
        return True

    def _start_batch_worker(self, worker, result_handler=None, connect_log=False):
        self.thread = QThread()
        self.worker = worker
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.on_batch_progress)
        self.worker.result.connect(result_handler or self.on_batch_result)
        self.worker.finished.connect(self.on_batch_finished)
        if connect_log and hasattr(self.worker, 'log'):
            self.worker.log.connect(self.on_batch_log)
        
        self.thread.finished.connect(self._cleanup_thread)
        self.thread.start()

    def _cleanup_thread(self):
        # This is called when the thread finishes to safely clear references
        # The thread and worker will be deleted by deleteLater() connected in _start_batch_worker
        self.thread = None
        self.worker = None

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("File")
        
        open_folder_action = QAction("Open Folder...", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)
        
        self.recent_menu = file_menu.addMenu("Recent Folders")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        import_csv_action = QAction("Import from CSV", self)
        import_csv_action.triggered.connect(self.import_from_csv)
        file_menu.addAction(import_csv_action)
        
        export_csv_action = QAction("Export to CSV", self)
        export_csv_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Quit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        
        global_edit_action = QAction("Edit all visible", self)
        global_edit_action.setShortcut("Ctrl+G")
        global_edit_action.triggered.connect(self.enter_global_mode)
        edit_menu.addAction(global_edit_action)
        
        edit_menu.addSeparator()
        
        case_menu = edit_menu.addMenu("Case Conversion")
        
        title_case_action = QAction("Title Case", self)
        title_case_action.triggered.connect(lambda: self.convert_case("title"))
        case_menu.addAction(title_case_action)
        
        upper_case_action = QAction("UPPERCASE", self)
        upper_case_action.triggered.connect(lambda: self.convert_case("upper"))
        case_menu.addAction(upper_case_action)
        
        lower_case_action = QAction("lowercase", self)
        lower_case_action.triggered.connect(lambda: self.convert_case("lower"))
        case_menu.addAction(lower_case_action)
        
        edit_menu.addSeparator()
        
        autotag_menu = edit_menu.addMenu("Auto-Tag")
        
        autotag_selected_action = QAction("Selected", self)
        autotag_selected_action.triggered.connect(self.autotag_selected)
        autotag_menu.addAction(autotag_selected_action)
        
        autotag_all_action = QAction("All Visible", self)
        autotag_all_action.triggered.connect(self.autotag_all)
        autotag_menu.addAction(autotag_all_action)
        
        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        
        lyrics_menu = tools_menu.addMenu("Lyrics")
        
        fetch_lyrics_action = QAction("Fetch lyrics (all visible)", self)
        fetch_lyrics_action.triggered.connect(self.fetch_all_lyrics)
        lyrics_menu.addAction(fetch_lyrics_action)
        
        romanize_all_action = QAction("Romanize lyrics (all visible)", self)
        romanize_all_action.triggered.connect(self.romanize_all)
        lyrics_menu.addAction(romanize_all_action)
        
        covers_menu = tools_menu.addMenu("Covers")
        
        fetch_covers_action = QAction("Fetch covers (all visible)", self)
        fetch_covers_action.triggered.connect(self.fetch_all_covers)
        covers_menu.addAction(fetch_covers_action)
        
        resize_selected_action = QAction("Resize covers (selected)", self)
        resize_selected_action.triggered.connect(self.resize_selected_covers)
        covers_menu.addAction(resize_selected_action)
        
        resize_all_action = QAction("Resize covers (all visible)", self)
        resize_all_action.triggered.connect(self.resize_all_covers)
        covers_menu.addAction(resize_all_action)
        
        file_actions_menu = tools_menu.addMenu("File Actions")
        
        rename_selected_action = QAction("Rename files (selected)", self)
        rename_selected_action.triggered.connect(self.rename_selected_files)
        file_actions_menu.addAction(rename_selected_action)
        
        rename_all_action = QAction("Rename files (all visible)", self)
        rename_all_action.triggered.connect(self.rename_all_files)
        file_actions_menu.addAction(rename_all_action)
        
        file_actions_menu.addSeparator()
        
        reencode_action = QAction("Re-encode FLAC (selected)", self)
        reencode_action.triggered.connect(self.reencode_flac_selected)
        file_actions_menu.addAction(reencode_action)
        
        reencode_all_action = QAction("Re-encode FLAC (all visible)", self)
        reencode_all_action.triggered.connect(self.reencode_flac_all)
        file_actions_menu.addAction(reencode_all_action)
        
        # View Menu
        view_menu = menu_bar.addMenu("View")
        
        view_by_menu = view_menu.addMenu("View By")
        
        view_file_action = QAction("File", self)
        view_file_action.triggered.connect(lambda: self.change_display_mode("File"))
        view_by_menu.addAction(view_file_action)
        
        view_album_action = QAction("Album", self)
        view_album_action.triggered.connect(lambda: self.change_display_mode("Album"))
        view_by_menu.addAction(view_album_action)
        
        view_artist_action = QAction("Artist", self)
        view_artist_action.triggered.connect(lambda: self.change_display_mode("Artist"))
        view_by_menu.addAction(view_artist_action)
        
        view_album_artist_action = QAction("Album Artist", self)
        view_album_artist_action.triggered.connect(lambda: self.change_display_mode("Album Artist"))
        view_by_menu.addAction(view_album_artist_action)
        
        view_menu.addSeparator()
        
        appearance_menu = view_menu.addMenu("Appearance")
        
        self.theme_action = QAction("Light Theme", self)
        self.theme_action.setCheckable(True)
        self.theme_action.triggered.connect(self.toggle_theme)
        appearance_menu.addAction(self.theme_action)
        

        
        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        
        hints_action = QAction("Hints and Tips", self)
        hints_action.triggered.connect(self.show_hints)
        help_menu.addAction(hints_action)
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About TagQt", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_display_mode(self, mode):
        self.file_list.set_display_mode(mode)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Check if we have selection
        files = self.get_selected_files()
        has_selection = len(files) > 0
        
        # Add actions from Tools menu
        
        # Covers
        get_covers_action = QAction("Fetch covers", self)
        # fetch_all_covers checks selection if global mode, but we might need to force it
        # Actually fetch_all_covers checks sidebar.is_global_mode. 
        # We should probably make a helper that respects selection regardless of mode for context menu.
        # But wait, the user said "when i right click a single song make get covers (selected) appears which should also work when i select all of them"
        # So context menu should always act on selection.
        
        # Let's create specific lambdas or methods for context menu that force using selection
        get_covers_action.triggered.connect(self.fetch_covers_context)
        get_covers_action.setEnabled(has_selection)
        menu.addAction(get_covers_action)
        
        resize_covers_action = QAction("Resize covers", self)
        resize_covers_action.triggered.connect(self.resize_selected_covers)
        resize_covers_action.setEnabled(has_selection)
        menu.addAction(resize_covers_action)
        
        menu.addSeparator()
        
        # Lyrics
        get_lyrics_action = QAction("Fetch lyrics", self)
        get_lyrics_action.triggered.connect(self.fetch_lyrics_context)
        get_lyrics_action.setEnabled(has_selection)
        menu.addAction(get_lyrics_action)
        
        romanize_action = QAction("Romanize lyrics", self)
        romanize_action.triggered.connect(self.romanize_context)
        romanize_action.setEnabled(has_selection)
        menu.addAction(romanize_action)
        
        menu.addSeparator()
        
        # File Actions
        rename_action = QAction("Rename files", self)
        rename_action.triggered.connect(self.rename_selected_files)
        rename_action.setEnabled(has_selection)
        menu.addAction(rename_action)
        
        reencode_action = QAction("Re-encode FLAC", self)
        reencode_action.triggered.connect(self.reencode_flac_selected)
        reencode_action.setEnabled(has_selection)
        menu.addAction(reencode_action)
        
        menu.addSeparator()
        
        autotag_action = QAction("Auto-tag from MusicBrainz", self)
        autotag_action.triggered.connect(self.autotag_selected)
        autotag_action.setEnabled(has_selection)
        menu.addAction(autotag_action)

        menu.exec_(self.file_list.mapToGlobal(pos))

    def fetch_covers_context(self):
        # Force selection usage
        files = self.get_selected_files()
        if not files: return
        self._fetch_covers_list(files)

    def fetch_lyrics_context(self):
        files = self.get_selected_files()
        if not files: return
        self._fetch_lyrics_list(files)

    def romanize_context(self):
        files = self.get_selected_files()
        if not files: return
        self._romanize_list(files)

    def enter_global_mode(self):
        # Select all VISIBLE files
        # First clear selection
        self.file_list.clearSelection()
        
        # Iterate and select visible
        iterator = QTreeWidgetItemIterator(self.file_list)
        has_visible = False
        while iterator.value():
            item = iterator.value()
            if not item.isHidden():
                item.setSelected(True)
                has_visible = True
            iterator += 1
            
        if not has_visible:
            self.show_toast("No visible files to edit. Open a folder first.")
        else:
            self.show_toast("Global edit — changes apply to all visible files.")



    def exit_global_mode(self):
        if not getattr(self.sidebar, 'is_global_mode', False):
            return  # Not in global mode, nothing to do
        
        self.sidebar.set_global_mode(False)
        
        files = self.get_selected_files()
        if files:
            first_file = files[0]
            
            iterator = QTreeWidgetItemIterator(self.file_list)
            found = False
            while iterator.value():
                item = iterator.value()
                if item.data(0, Qt.UserRole) == first_file:
                    self.file_list.clearSelection()
                    self.file_list.setCurrentItem(item)
                    item.setSelected(True)
                    found = True
                    break
                iterator += 1
            
            if found:
                self.load_file(first_file)
            else:
                self.file_list.clearSelection()
        else:
            self.file_list.clearSelection()
        
        self.show_toast("Exited global edit.")

    def get_selected_files(self):
        # Helper to get selected files from FileList
        # Currently FileList is single selection mostly, but we should support multi-selection for tools
        # For now, let's just use the current file if single, or all files if we implement multi-select later.
        # But wait, FileList is a QTreeWidget.
        selected_items = self.file_list.selectedItems()
        files = []
        for item in selected_items:
            filepath = item.data(0, Qt.UserRole)
            if filepath:
                files.append(filepath)
            else:
                # It's a group, maybe add children?
                for i in range(item.childCount()):
                    child = item.child(i)
                    fp = child.data(0, Qt.UserRole)
                    if fp:
                        files.append(fp)
        return list(set(files)) # Unique
        
    def get_all_files(self):
        # Helper to get all files in the list
        # MODIFIED: Only return VISIBLE files to support scoped bulk operations
        files = []
        iterator = QTreeWidgetItemIterator(self.file_list)
        while iterator.value():
            item = iterator.value()
            # Check if item is hidden
            if not item.isHidden():
                filepath = item.data(0, Qt.UserRole)
                if filepath:
                    files.append(filepath)
            iterator += 1
        return list(set(files))



    def show_batch_details(self):
        if not self._status_is_batch:
            return
            
        if self.batch_dialog:
            self.batch_dialog.show()
            self.batch_dialog.raise_()
            self.batch_dialog.activateWindow()

    def fetch_all_lyrics(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            files = self.get_selected_files()
        else:
            files = self.get_all_files()
        self._fetch_lyrics_list(files)

    def _fetch_lyrics_list(self, files):
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
            
        if not self._prepare_batch("Get Lyrics Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Fetching lyrics"
        self.progress_label.setText("Fetching lyrics… 0%")
        
        self._start_batch_worker(LyricsWorker(files, self.lyrics_fetcher), connect_log=True)

    def on_batch_progress(self, current, total):
        if total > 0:
            target_value = int((current / total) * 100)
            self.progress_bar.setMaximum(100)
            
            if hasattr(self, '_progress_animation'):
                from PySide6.QtCore import QPropertyAnimation
                if self._progress_animation.state() == QPropertyAnimation.Running:
                    self._progress_animation.stop()
                
                self._progress_animation.setStartValue(self.progress_bar.value())
                self._progress_animation.setEndValue(target_value)
                self._progress_animation.start()
            else:
                self.progress_bar.setValue(target_value)
            
            # Use stored operation label, with near-completion message
            op = getattr(self, '_batch_op_label', 'Working')
            if target_value >= 90:
                self.progress_label.setText(f"Almost done… {target_value}%")
            else:
                self.progress_label.setText(f"{op}… {target_value}%")
        self.batch_dialog.update_progress(current, total)
        
    def on_batch_result(self, filepath, status, message):
        self.batch_dialog.add_result(filepath, status, message)
        if status in ["Updated", "Success", "Found"]:
            self.file_list.update_file(filepath)
        
    def on_batch_log(self, message):
        import logging
        logging.getLogger(__name__).debug(message)
    
    def cancel_batch_operation(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
        
        self.batch_cancel_btn.setEnabled(False)
        self.batch_cancel_btn.setText("Stopping…")
        
        if hasattr(self, 'thread') and self.thread and self.thread.isRunning():
            self.thread.finished.connect(self._on_cancel_complete)
        else:
            self._on_cancel_complete()

    def _on_cancel_complete(self):
        self.batch_container.setVisible(False)
        self.batch_cancel_btn.setVisible(False)
        self.batch_cancel_btn.setEnabled(True)
        self.batch_cancel_btn.setText("Cancel")
        self._persistent_toast = None
        self.show_toast("Canceled.", duration=3000)
        
    def on_batch_finished(self):
        self.batch_running = False
        self.batch_dialog.set_finished()
        # self.batch_container.setVisible(False) # Keep visible for persistence
        self.batch_cancel_btn.setVisible(False)
        self.progress_label.setText("Done — click for details")
        self.progress_bar.setValue(self.progress_bar.maximum())
        
        # Auto-exit global mode after a global save completes
        if getattr(self, '_global_save_pending', False):
            self._global_save_pending = False
            self.exit_global_mode()
        
        # Generate detailed summary
        results = self.batch_dialog.results
        total = len(results)
        
        if total == 0:
            self.show_toast("Nothing to process.", is_batch=True)
            return

        success_count = len([r for r in results if r['status'] in ['Success', 'Updated', 'Found', 'Renamed']])
        skipped_count = len([r for r in results if r['status'] == 'Skipped'])
        error_count = len([r for r in results if r['status'] in ['Error', 'Missing', 'Failed']])
        
        if skipped_count == total:
            msg = f"All {total} files already up to date."
        elif success_count == total:
            msg = f"All done — updated {total} files."
        elif error_count == total:
            msg = f"{total} files had errors. Click the bar for details."
        else:
            parts = []
            if success_count > 0: parts.append(f"Updated {success_count}")
            if skipped_count > 0: parts.append(f"Skipped {skipped_count}")
            if error_count > 0: parts.append(f"Failed {error_count}")
            msg = "Done — " + ", ".join(parts).lower()
            
        self.show_toast(msg, is_batch=True)
        
        # If we are in a grouped mode, we need a full refresh at the end
        # to ensure items are in the correct groups if their tags changed.
        if self.file_list.current_mode != "File":
            self.file_list.refresh_view()
            
        if self.current_file:
             self.load_file(self.current_file)

    def fetch_all_covers(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            files = self.get_selected_files()
        else:
            files = self.get_all_files()
        self._fetch_covers_list(files)

    def _fetch_covers_list(self, files):
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
            
        if not self._prepare_batch("Get Covers Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Fetching covers"
        self.progress_label.setText("Fetching covers… 0%")
        
        self._start_batch_worker(CoverFetchWorker(files, self.cover_manager))

    def resize_selected_covers(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Select some files first.")
            return
        self._resize_covers(files)

    def resize_all_covers(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
        self._resize_covers(files)

    def _resize_covers(self, files):
        if not self._prepare_batch("Resize Covers Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Resizing covers"
        self.progress_label.setText("Resizing covers… 0%")
        
        self._start_batch_worker(CoverResizeWorker(files))

    def romanize_all(self):
        files = self.get_all_files()
        self._romanize_list(files)

    def _romanize_list(self, files):
        available, msg = DependencyChecker.check_koroman()
        if not available:
            dialogs.show_error(self, "Missing Tool", msg)
            return
        
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
            
        if not self._prepare_batch("Romanize Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Romanizing lyrics"
        self.progress_label.setText("Romanizing lyrics… 0%")
        
        self._start_batch_worker(RomanizeWorker(files, self.romanizer))

    def open_rename_dialog(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Select the files you want to rename.")
            return
        self._show_rename_dialog(files)

    def rename_selected_files(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Select the files you want to rename.")
            return
        self._show_rename_dialog(files)

    def rename_all_files(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
        self._show_rename_dialog(files)

    def _show_rename_dialog(self, files):
        # We need metadata for preview
        file_data = []
        for f in files:
            md = MetadataHandler(f)
            file_data.append((f, md))
            
        from tagqt.ui.rename import RenamerDialog
        dialog = RenamerDialog(file_data, self)
        if dialog.exec():
            rename_data = dialog.preview_data
            if not rename_data:
                return

            if not self._prepare_batch("Renaming Files"):
                return
            
            self.progress_bar.setRange(0, len(rename_data))
            self._batch_op_label = "Renaming files"
            self.progress_label.setText("Renaming files… 0%")
            
            self._start_batch_worker(RenameWorker(rename_data), result_handler=self.on_rename_result)

    def on_rename_result(self, old_path, status, message):
        self.batch_dialog.add_result(old_path, status, message)
        if status == "Success":
            # Extract new path from message "Renamed to ..."
            new_name = message.replace("Renamed to ", "")
            dir_path = os.path.dirname(old_path)
            new_path = os.path.join(dir_path, new_name)
            
            self.file_list.rename_file(old_path, new_path)
            
            if self.current_file == old_path:
                self.current_file = new_path
                # We don't load_file here to avoid UI flicker during batch
                # It will be loaded in on_batch_finished if it was the current file

    def convert_case(self, mode):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Select some files first.")
            return
            
        if not self._prepare_batch("Case Conversion Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Converting case"
        self.progress_label.setText("Converting case… 0%")
        
        self._start_batch_worker(CaseConvertWorker(files, mode))

    def reencode_flac_selected(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Select the FLAC files you want to re-encode.")
            return
        self._reencode_flac_files(files)

    def reencode_flac_all(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
        self._reencode_flac_files(files)

    def _reencode_flac_files(self, files):
        available, msg = DependencyChecker.check_flac_tools()
        if not available:
            dialogs.show_error(self, "Missing Dependency", msg)
            return
        
        flac_files = [f for f in files if f.lower().endswith('.flac')]
        if not flac_files:
            dialogs.show_warning(self, "No FLAC Files", "None of the selected files are FLAC. Pick some FLAC files and try again.")
            return
        
        if not self._prepare_batch("Re-encode FLAC Status"):
            return
            
        self.progress_bar.setRange(0, len(flac_files))
        self._batch_op_label = "Re-encoding FLAC"
        self.progress_label.setText("Re-encoding FLAC… 0%")
        
        self._start_batch_worker(FlacReencodeWorker(flac_files))

    def export_to_csv(self):
        files = self.file_list.all_files
        if not files:
            dialogs.show_warning(self, "No Files", "Load some audio files before exporting.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export metadata to CSV", "", "CSV Files (*.csv)")
        if not filepath:
            return
        
        from tagqt.core.csv_io import export_metadata_to_csv
        success, error = export_metadata_to_csv(files, filepath)
        if success:
            self.show_toast(f"Exported {len(files)} files to CSV.")
        else:
            dialogs.show_warning(self, "Couldn't Export", error)

    def import_from_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import metadata from CSV", "", "CSV Files (*.csv)")
        if not filepath:
            return
        
        from tagqt.core.csv_io import import_metadata_from_csv
        rows, error = import_metadata_from_csv(filepath)
        if error:
            dialogs.show_warning(self, "Couldn't Import", error)
            return
        
        if not self._prepare_batch("CSV Import Status"):
            return
            
        self.progress_bar.setRange(0, len(rows))
        self._batch_op_label = "Importing CSV"
        self.progress_label.setText("Importing CSV… 0%")
        
        self._start_batch_worker(CsvImportWorker(rows))

    def autotag_selected(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Files", "Select some files first.")
            return
        self._autotag_files(files)
    
    def autotag_all(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "Open a folder to load audio files first.")
            return
        self._autotag_files(files)
    
    def _autotag_files(self, files):
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Auto-Tag")
        msg.setText(f"Auto-tag {len(files)} files from MusicBrainz?")
        msg.setInformativeText("What about files that already have tags?")
        
        skip_btn = msg.addButton("Skip tagged", QMessageBox.AcceptRole)
        all_btn = msg.addButton("Tag everything", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.setDefaultButton(skip_btn)
        msg.setStyleSheet(self.styleSheet())
        
        msg.exec()
        
        clicked = msg.clickedButton()
        if clicked == cancel_btn:
            return
            
        skip_existing = (clicked == skip_btn)
        
        if not self._prepare_batch("Auto-Tag Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self._batch_op_label = "Auto-tagging"
        self.progress_label.setText("Auto-tagging… 0%")
        
        self._start_batch_worker(AutoTagWorker(files, skip_existing=skip_existing), connect_log=True)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder_path:
            self.load_folder(folder_path)

    def load_folder(self, folder_path):
        if not self._prepare_batch("Loading Folder"):
            return
            
        self._batch_op_label = "Scanning folder"
        self.progress_label.setText("Scanning folder…")
        self.progress_bar.setRange(0, 0) # Indeterminate
        
        # Create Thread and Worker
        self.thread = QThread()
        self.worker = FolderLoaderWorker(folder_path)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.finished.connect(self.on_folder_loaded)
        
        # Start
        self.thread.start()

    def on_folder_loaded(self, results, folder_path):
        self.batch_container.setVisible(False)
        self.file_list.clear_files()
        if results:
            self.file_list.add_files(results)
        
        self.settings.add_recent_folder(folder_path)
        self.update_recent_menu()
        
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.batch_running = False
        
        # Add result to batch dialog for details
        if results:
            self.batch_dialog.add_result(folder_path, "Success", f"Loaded {len(results)} files.")
        else:
            self.batch_dialog.add_result(folder_path, "Skipped", "No audio files found.")
        self.batch_dialog.set_finished()
        self.batch_cancel_btn.setVisible(False)
        
        if results:
            self.show_toast(f"{len(results)} files loaded from {os.path.basename(folder_path)}.", is_batch=True)
        else:
             self.show_toast(f"No audio files in {os.path.basename(folder_path)}.", is_batch=False)

    def update_recent_menu(self):
        self.recent_menu.clear()
        folders = self.settings.get_recent_folders()
        
        if not folders:
            no_recent = QAction("No recent folders", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            for folder in folders:
                action = QAction(folder, self)
                action.triggered.connect(lambda checked, f=folder: self.load_folder(f))
                self.recent_menu.addAction(action)
            
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent", self)
            clear_action.triggered.connect(self.clear_recent_folders)
            self.recent_menu.addAction(clear_action)
    
    def clear_recent_folders(self):
        self.settings.clear_recent_folders()
        self.update_recent_menu()

    def toggle_theme(self, checked):
        Theme.set_light_mode(checked)
        self.settings.set_light_theme(checked)
        self._apply_theme()

    def _apply_theme(self):
        self.setUpdatesEnabled(False)
        try:
            stylesheet = Theme.get_stylesheet()
            self.setStyleSheet(stylesheet)
            self.sidebar.setStyleSheet(stylesheet)
            self.sidebar.apply_theme()
            
            self.title_label.setStyleSheet("background: transparent;")
            
            self.batch_cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.SURFACE1};
                    color: {Theme.TEXT};
                    font-size: 11px;
                    font-weight: 600;
                    border: 1px solid {Theme.SURFACE1};
                    border-radius: 4px;
                    padding: 4px 12px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.RED};
                    color: {Theme.TOAST_TEXT};
                    border: 1px solid {Theme.RED};
                }}
                QPushButton:pressed {{
                    background-color: {Theme.ACCENT_DIM};
                }}
                QPushButton:disabled {{
                    background-color: {Theme.SURFACE2};
                    color: {Theme.SUBTEXT0};
                }}
            """)
            
            self.progress_frame.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border-radius: 6px;
                    border: none;
                }}
                QWidget:hover {{
                    background-color: {Theme.SURFACE0};
                }}
            """)
            
            self.progress_label.setStyleSheet(f"""
                QLabel {{
                    color: {Theme.SUBTEXT1};
                    font-size: 12px;
                    font-weight: normal;
                    background: transparent;
                    border: none;
                }}
            """)
            
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: {Theme.SURFACE0};
                    border-radius: 3px;
                    min-height: 6px;
                    max-height: 6px;
                }}
                QProgressBar::chunk {{
                    background-color: {Theme.ACCENT};
                    border-radius: 3px;
                }}
            """)
            
            # Player bar theme refresh
            if hasattr(self, 'player_bar_widget'):
                self.player_bar_widget.setStyleSheet(f"""
                    QWidget#playerBar {{
                        background-color: {Theme.CRUST};
                        border-top: 1px solid {Theme.SURFACE1};
                    }}
                """)
                
                transport_style = f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Theme.TEXT};
                        border: none;
                        font-size: 16px;
                        padding: 4px 8px;
                        min-height: 22px;
                        min-width: 28px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.SURFACE0};
                        border-radius: 4px;
                    }}
                    QPushButton:pressed {{
                        background-color: {Theme.SURFACE1};
                    }}
                """
                for btn in (self.btn_prev, self.btn_play, self.btn_stop, self.btn_next):
                    btn.setStyleSheet(transport_style)
                
                self.time_label.setStyleSheet(f"""
                    QLabel {{
                        color: {Theme.SUBTEXT0};
                        font-size: 11px;
                        background: transparent;
                        border: none;
                        min-width: 80px;
                    }}
                """)
                self.now_playing_label.setStyleSheet(f"""
                    QLabel {{
                        color: {Theme.SUBTEXT1};
                        font-size: 12px;
                        background: transparent;
                        border: none;
                    }}
                """)
                self._vol_label.setStyleSheet(f"color: {Theme.SUBTEXT0}; font-size: 13px; background: transparent; border: none;")
            
            if hasattr(self, 'toast_manager') and self.toast_manager.current_toast:
                self.toast_manager.current_toast.close()
        finally:
            self.setUpdatesEnabled(True)

    def show_hints(self):
        hints_text = """
<b>Batch Operations</b>
<ul>
<li>Select multiple files to enter Global Edit mode</li>
<li>Click the progress bar to view operation details</li>
<li>Right-click files for context menu actions</li>
</ul>

<b>Editing</b>
<ul>
<li>Global Edit applies changes to all selected files</li>
<li>Right-click column headers to show/hide columns</li>
<li>Empty fields in Global Edit keep the original value</li>
</ul>

<b>Optional Dependencies</b>
<ul>
<li><code>koroman</code> - Korean romanization</li>
<li><code>ffmpeg</code> - FLAC re-encoding</li>
<li><code>musicbrainzngs</code> - Auto-tagging</li>
</ul>

<b>Formats</b>: MP3, FLAC, OGG, M4A, WAV
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.setWindowTitle("Hints and Tips")
        dialog.set_content(hints_text)
        dialog.exec()
    
    def show_shortcuts(self):
        shortcuts_text = """
<table width="100%" cellpadding="10" style="border-collapse: collapse;">
<tr><td width="120"><code>Ctrl+O</code></td><td>Open folder</td></tr>
<tr><td><code>Ctrl+S</code></td><td>Save changes</td></tr>
<tr><td><code>Ctrl+G</code></td><td>Toggle Global Edit</td></tr>
<tr><td><code>Ctrl+A</code></td><td>Select all files</td></tr>
<tr><td><code>Escape</code></td><td>Exit Global Edit</td></tr>
<tr><td><code>Ctrl+Q</code></td><td>Quit</td></tr>
</table>
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.set_content(shortcuts_text)
        dialog.exec()
    
    def show_about(self):
        import os, base64
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtGui import QPixmap, QPainter
        from PySide6.QtCore import QBuffer, QIODevice
        
        import sys
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, 'assets', 'logo.svg')
        else:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'logo.svg')
        renderer = QSvgRenderer(logo_path)
        svg_size = renderer.defaultSize()
        target_h = 48
        target_w = int(svg_size.width() * target_h / svg_size.height())
        logo_pixmap = QPixmap(target_w, target_h)
        logo_pixmap.fill(Qt.transparent)
        painter = QPainter(logo_pixmap)
        renderer.render(painter)
        painter.end()
        
        # Convert pixmap to base64 for HTML embedding
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        logo_pixmap.save(buffer, "PNG")
        logo_b64 = base64.b64encode(buffer.data().data()).decode()
        
        from tagqt.version import __version__
        about_text = f"""
<div style="text-align: center; margin-bottom: 10px;">
<img src="data:image/png;base64,{logo_b64}" width="{target_w}" height="{target_h}"><br>
<span style="color: {Theme.SUBTEXT0};">v{__version__}</span>
</div>

<p>A fast, modern music tag editor. Edit metadata, fetch lyrics and covers,
auto-tag from MusicBrainz, batch rename files — all in one place.</p>

<p>Supports MP3, FLAC, OGG, M4A, and WAV.</p>

<p style="margin-top: 20px;">
<a href="https://github.com/selr1/tagqt" style="color: {Theme.ACCENT};">github.com/selr1/tagqt</a>
</p>
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.setWindowTitle("About TagQt")
        dialog.set_content(about_text)
        dialog.exec()



    def on_files_dropped(self, files):
        if files:
            for f in files:
                self.file_list.add_file(f)
            # Load the first one
            self.load_file(files[0])

    def on_filter_changed(self, text):
        """Debounce filter input to avoid refiltering on every keystroke."""
        self.filter_timer.start()

    def _apply_filter(self):
        """Apply the current filter text to the file list."""
        self.file_list.set_filter(self.filter_input.text())

    def on_selection_changed(self):
        # Restart timer (debounce) - waits for selection to stabilize
        self.selection_timer.start(100) # 100ms delay

    def _handle_selection_deferred(self):
        files = self.get_selected_files()
        
        if len(files) > 1:
            self.sidebar.set_global_mode(True)
            self.current_file = None 
            self.metadata = None
        elif len(files) == 1:
            self.sidebar.set_global_mode(False)
            self.load_file(files[0])
        else:
            self.sidebar.set_global_mode(False)
            
    def load_file(self, filepath):
        self.current_file = filepath
        self.metadata = MetadataHandler(filepath)
        self.populate_sidebar()

    def populate_sidebar(self):
        if not self.metadata:
            return
        
        self.sidebar.title_edit.setText(self.metadata.title)
        self.sidebar.artist_edit.setText(self.metadata.artist)
        self.sidebar.album_edit.setText(self.metadata.album)
        self.sidebar.album_artist_edit.setText(self.metadata.album_artist)
        self.sidebar.year_edit.setText(self.metadata.year)
        self.sidebar.genre_edit.setText(self.metadata.genre)
        self.sidebar.disc_edit.setText(self.metadata.disc_number)
        self.sidebar.track_edit.setText(self.metadata.track_number)
        self.sidebar.comment_edit.setText(self.metadata.comment)
        self.sidebar.lyrics_edit.setText(self.metadata.lyrics)
        
        # Extended
        self.sidebar.bpm_edit.setText(self.metadata.bpm)
        self.sidebar.key_edit.setText(self.metadata.initial_key)
        self.sidebar.isrc_edit.setText(self.metadata.isrc)
        self.sidebar.publisher_edit.setText(self.metadata.publisher)
        
        # Load cover
        cover_data = self.metadata.get_cover()
        if cover_data:
            pixmap = QPixmap()
            pixmap.loadFromData(cover_data)
            self.sidebar.set_cover(pixmap)
        else:
            self.sidebar.set_cover(None)
            
        # Set specs
        specs = {
            'bitrate': self.metadata.bitrate,
            'sample_rate': self.metadata.sample_rate,
            'filesize': self.metadata.filesize
        }
        self.sidebar.set_file_specs(specs)

    def save_metadata(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            files = self.get_selected_files()
            if not files:
                return
                
            changes = self.sidebar.get_modified_fields()
            if not changes:
                self.show_toast("Nothing changed.")
                return
                
            if not self._prepare_batch("Global Save Status"):
                return
            self.progress_bar.setRange(0, len(files))
            self._batch_op_label = "Saving changes"
            self.progress_label.setText("Saving changes… 0%")
            
            self._global_save_pending = True
            self._start_batch_worker(SaveWorker(files, changes))
            
        else:
            # Single file save
            if not self.metadata:
                return
                
            self.metadata.title = self.sidebar.title_edit.text()
            self.metadata.artist = self.sidebar.artist_edit.text()
            self.metadata.album = self.sidebar.album_edit.text()
            self.metadata.album_artist = self.sidebar.album_artist_edit.text()
            self.metadata.year = self.sidebar.year_edit.text()
            self.metadata.genre = self.sidebar.genre_edit.text()
            self.metadata.disc_number = self.sidebar.disc_edit.text()
            self.metadata.track_number = self.sidebar.track_edit.text()
            self.metadata.comment = self.sidebar.comment_edit.text()
            self.metadata.lyrics = self.sidebar.lyrics_edit.toPlainText()
            
            # Extended
            self.metadata.bpm = self.sidebar.bpm_edit.text()
            self.metadata.initial_key = self.sidebar.key_edit.text()
            self.metadata.isrc = self.sidebar.isrc_edit.text()
            self.metadata.publisher = self.sidebar.publisher_edit.text()
            
            self.metadata.save()
            
            # Save cover.jpg if we have cover data (always overwrite on manual save)
            if self.metadata.get_cover():
                self.metadata.save_cover_file(overwrite=True)
                
            self.show_toast("Saved.")
            
            # Refresh the item in the list
            self.file_list.update_file(self.current_file)

    def romanize_metadata(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            # Process strictly selected files in global mode
            files = self.get_selected_files()
            if files:
                self._romanize_list(files)
            else:
                dialogs.show_warning(self, "No Selection", "Select the files you want to romanize.")
            return
            
        available, msg = DependencyChecker.check_koroman()
        if not available:
            dialogs.show_error(self, "Missing Tool", msg)
            return
        self.sidebar.lyrics_edit.setText(self.romanizer.romanize_text(self.sidebar.lyrics_edit.toPlainText()))

    def fetch_lyrics(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            self.fetch_all_lyrics()
            return
            
        artist = self.sidebar.artist_edit.text()
        title = self.sidebar.title_edit.text()
        album = self.sidebar.album_edit.text()
        
        from tagqt.ui.search import UnifiedSearchDialog
        
        def search_callback(a, t, al):
            return self.lyrics_fetcher.search_lyrics(a, t, al)
            
        dialog = UnifiedSearchDialog(self, mode="lyrics", initial_artist=artist, initial_title=title, initial_album=album, fetcher_callback=search_callback)
        
        if dialog.exec() == QDialog.Accepted and dialog.selected_result:
            res = dialog.selected_result
            lyrics = res.get("syncedLyrics") or res.get("plainLyrics")
            if lyrics:
                self.sidebar.lyrics_edit.setText(lyrics)
                self.show_toast("Lyrics loaded — save to keep them.")
            else:
                dialogs.show_warning(self, "No Lyrics", "That result doesn't have any lyrics text.")

    def search_cover(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            self.fetch_all_covers()
            return
            
        artist = self.sidebar.artist_edit.text()
        album = self.sidebar.album_edit.text()
        
        from tagqt.ui.search import UnifiedSearchDialog
        
        def search_callback(a, al):
            return self.cover_manager.search_cover_candidates(a, al)
            
        dialog = UnifiedSearchDialog(self, mode="cover", initial_artist=artist, initial_album=album, fetcher_callback=search_callback)
        
        if dialog.exec() == QDialog.Accepted and dialog.selected_result:
            res = dialog.selected_result
            url = res.get("url")
            
            try:
                data = self.cover_manager.download_and_process_cover(url)
                if data:
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    self.sidebar.set_cover(pixmap)
                    
                    if self.metadata:
                        self.metadata.set_cover(data)
            except Exception as e:
                dialogs.show_error(self, "Download Failed", f"Couldn't download that cover. {e}")

    def load_cover_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load cover from file", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Validate image
                pixmap = QPixmap()
                if pixmap.loadFromData(data):
                    self.sidebar.set_cover(pixmap)
                    if self.metadata:
                        self.metadata.set_cover(data)
                else:
                    dialogs.show_warning(self, "Unrecognized Image", "That file doesn't look like a valid image. Try a different one.")
            except Exception as e:
                dialogs.show_error(self, "Couldn't Load Cover", f"Something went wrong reading that file. {e}")

    def load_lyrics_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load lyrics from file", "", "Lyrics (*.lrc *.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lyrics = f.read()
                
                self.sidebar.lyrics_edit.setText(lyrics)
            except Exception as e:
                dialogs.show_error(self, "Couldn't Load Lyrics", f"Something went wrong reading that file. {e}")

    # ── Player helpers ──────────────────────────────────────────────────

    def _build_play_queue(self) -> list[str]:
        """Return filepaths in the exact visual order of the QTreeWidget."""
        paths = []
        iterator = QTreeWidgetItemIterator(self.file_list)
        while iterator.value():
            item = iterator.value()
            if not item.isHidden():
                filepath = item.data(0, Qt.UserRole)
                if filepath and isinstance(filepath, str):
                    paths.append(filepath)
            iterator += 1
        return paths

    def _on_tree_double_click(self, item, column):
        """Start playback from the double-clicked track."""
        filepath = item.data(0, Qt.UserRole)
        if not filepath:
            return
        queue = self._build_play_queue()
        if filepath not in queue:
            return
        idx = queue.index(filepath)
        self.player.set_queue(queue, idx)
        self.player.play_pause()
        self._on_player_track_changed(idx)
        self._lyrics_sync_paused = False

    def _on_play_btn_clicked(self):
        """Play button clicked — start from selection if nothing queued."""
        if self.player.current_index < 0:
            queue = self._build_play_queue()
            if not queue:
                return
            # Use selected item if there is one, otherwise start from top
            selected = self.file_list.selectedItems()
            start = 0
            if selected:
                fp = selected[0].data(0, Qt.UserRole)
                if fp and fp in queue:
                    start = queue.index(fp)
            self.player.set_queue(queue, start)
            self._on_player_track_changed(start)
            self._lyrics_sync_paused = False
        self.player.play_pause()

    def _on_player_state_changed(self, state):
        if state == 'playing':
            self.btn_play.setText('⏸')
            self.btn_play.setToolTip('Pause')
        else:
            self.btn_play.setText('▶')
            self.btn_play.setToolTip('Play')
        if state == 'stopped' and self.player.current_index >= len(self._build_play_queue()) - 1:
            self.now_playing_label.setText('')
            self._clear_lyric_highlights()

    def _on_player_track_changed(self, index):
        queue = self._build_play_queue()
        if 0 <= index < len(queue):
            path = queue[index]
            basename = os.path.basename(path)
            name, _ = os.path.splitext(basename)
            self.now_playing_label.setText(name)
            self.now_playing_label.setToolTip(basename)
        
        # Remove bold from previous item
        if self._now_playing_item:
            try:
                font = self._now_playing_item.font(0)
                font.setBold(False)
                for col in range(self._now_playing_item.columnCount()):
                    self._now_playing_item.setFont(col, font)
            except RuntimeError:
                pass
            self._now_playing_item = None
        
        # Bold the new now-playing row
        if 0 <= index < len(queue):
            path = queue[index]
            if path in self.file_list.path_to_item:
                item = self.file_list.path_to_item[path]
                font = item.font(0)
                font.setBold(True)
                for col in range(item.columnCount()):
                    item.setFont(col, font)
                self._now_playing_item = item
                self.file_list.scrollToItem(item)
        
        # Load lyrics for the new track into the player for sync
        if 0 <= index < len(queue):
            path = queue[index]
            try:
                meta = MetadataHandler(path)
                lrc_text = meta.lyrics or ''
                self.player.set_lyrics(lrc_text)
            except Exception:
                self.player.set_lyrics('')

    def _on_player_position_changed(self, current_ms, total_ms):
        if not self.seek_slider.isSliderDown():
            self.seek_slider.setMaximum(max(total_ms, 0))
            self.seek_slider.setValue(current_ms)
        
        def fmt(ms):
            s = max(ms, 0) // 1000
            return f"{s // 60}:{s % 60:02d}"
        
        self.time_label.setText(f"{fmt(current_ms)} / {fmt(total_ms)}")

    def _on_lyric_line_changed(self, index: int):
        """Highlight the current lyric line in the sidebar lyrics editor."""
        if self._lyrics_sync_paused:
            return

        lrc_lines = self.player._lrc_lines
        if not lrc_lines or index < 0 or index >= len(lrc_lines):
            return

        lyrics_edit = self.sidebar.lyrics_edit
        if not lyrics_edit.toPlainText():
            return

        lyrics_edit.blockSignals(True)
        try:
            doc = lyrics_edit.document()

            # Clear all existing highlighting
            cursor_clear = QTextCursor(doc)
            cursor_clear.select(QTextCursor.SelectionType.Document)
            fmt_clear = QTextCharFormat()
            fmt_clear.setBackground(QColor("transparent"))
            fmt_clear.setForeground(QColor(Theme.TEXT))
            cursor_clear.setCharFormat(fmt_clear)

            # Navigate to the line by index
            cursor_line = QTextCursor(doc)
            cursor_line.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(index):
                cursor_line.movePosition(QTextCursor.MoveOperation.NextBlock)

            # Select the entire line
            cursor_line.movePosition(
                QTextCursor.MoveOperation.EndOfBlock,
                QTextCursor.MoveMode.KeepAnchor
            )

            # Apply highlight with accent background
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(Theme.SURFACE1))
            fmt.setForeground(QColor(Theme.ACCENT))
            fmt.setFontWeight(QFont.Weight.Bold)
            cursor_line.setCharFormat(fmt)

            # Scroll to the highlighted line
            lyrics_edit.setTextCursor(cursor_line)
            lyrics_edit.ensureCursorVisible()
        finally:
            lyrics_edit.blockSignals(False)

    def _clear_lyric_highlights(self):
        """Remove all lyric highlight formatting."""
        lyrics_edit = self.sidebar.lyrics_edit
        if not lyrics_edit.toPlainText():
            return
        lyrics_edit.blockSignals(True)
        try:
            cursor = QTextCursor(lyrics_edit.document())
            cursor.select(QTextCursor.SelectionType.Document)
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("transparent"))
            fmt.setForeground(QColor(Theme.TEXT))
            cursor.setCharFormat(fmt)
        finally:
            lyrics_edit.blockSignals(False)

    def eventFilter(self, obj, event):
        """Pause lyrics sync when user interacts with the sidebar."""
        if obj is self.sidebar:
            if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.FocusIn):
                self._lyrics_sync_paused = True
        return super().eventFilter(obj, event)
