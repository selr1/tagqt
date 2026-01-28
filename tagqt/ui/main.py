from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QComboBox, QMenuBar, QMenu, QTreeWidgetItemIterator, QDialog, QProgressBar, QSizePolicy
from PySide6.QtGui import QPixmap, QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer, QThread, QEvent
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
        self.setWindowTitle("TagQt")
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
        
        self.title_label = QLabel("TagQt")
        self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.ACCENT};")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Notification Area (Right Aligned)
        self.notification_layout = QHBoxLayout()
        self.notification_layout.setSpacing(15)
        
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
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {Theme.RED};
                color: #ffffff;
                border: 1px solid {Theme.RED};
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
        
        frame_layout = QHBoxLayout(self.progress_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFixedHeight(20) # Height for text
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {Theme.SURFACE0};
                border-radius: 4px;
                color: {Theme.TEXT}; /* Text color on empty part */
                font-size: 11px;
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 4px;
            }}
        """)
        # Set selection color (text color on filled part) via palette or stylesheet if supported
        # Qt stylesheet 'selection-color' works for QProgressBar in some styles, but let's try it.
        # Also 'color' is usually for the unfilled part.
        # To ensure contrast on the filled part (Accent), we want CRUST or White.
        # Theme.CRUST is black-ish, Theme.ACCENT is pink/red. Black on Pink is good.
        self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + f"""
            QProgressBar {{
                selection-color: {Theme.CRUST};
                selection-background-color: {Theme.ACCENT};
            }}
        """)
        frame_layout.addWidget(self.progress_bar)

        batch_layout.addWidget(self.progress_frame)
        
        self.notification_layout.addWidget(self.batch_container)
        
        header_layout.addLayout(self.notification_layout)
        
        main_layout.addLayout(header_layout)

        # Content Layout (Horizontal)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # File List (Left/Center)
        self.file_list = FileList()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.files_dropped.connect(self.on_files_dropped)
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        content_layout.addWidget(self.file_list, stretch=2)
        
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

    def closeEvent(self, event):
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
        super().closeEvent(event)

    def on_progress_click(self, event):
        self.show_batch_details()

    def show_toast(self, message, duration=3000, is_batch=False):
        # Use new ToastManager
        # If is_batch is True, it might be a persistent status update?
        # The user said "move new toast to another place".
        # We'll use the overlay for all toasts.
        self.toast_manager.show_message(message, duration)
    
    def _hide_toast(self):
        pass # No longer needed with ToastManager

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
                dialogs.show_warning(self, "Busy", "Another operation is already in progress. Please wait for the previous one to finish.")
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
        self.progress_bar.setFormat("Starting...")
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
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        
        global_edit_action = QAction("Global Edit (All Visible)", self)
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
        
        fetch_lyrics_action = QAction("Get Lyrics (All Visible)", self)
        fetch_lyrics_action.triggered.connect(self.fetch_all_lyrics)
        lyrics_menu.addAction(fetch_lyrics_action)
        
        romanize_all_action = QAction("Romanize Lyrics (All Visible)", self)
        romanize_all_action.triggered.connect(self.romanize_all)
        lyrics_menu.addAction(romanize_all_action)
        
        covers_menu = tools_menu.addMenu("Covers")
        
        fetch_covers_action = QAction("Get Covers (All Visible)", self)
        fetch_covers_action.triggered.connect(self.fetch_all_covers)
        covers_menu.addAction(fetch_covers_action)
        
        resize_selected_action = QAction("Resize Covers (Selected)", self)
        resize_selected_action.triggered.connect(self.resize_selected_covers)
        covers_menu.addAction(resize_selected_action)
        
        resize_all_action = QAction("Resize Covers (All Visible)", self)
        resize_all_action.triggered.connect(self.resize_all_covers)
        covers_menu.addAction(resize_all_action)
        
        file_actions_menu = tools_menu.addMenu("File Actions")
        
        rename_selected_action = QAction("Rename Files (Selected)", self)
        rename_selected_action.triggered.connect(self.rename_selected_files)
        file_actions_menu.addAction(rename_selected_action)
        
        rename_all_action = QAction("Rename Files (All Visible)", self)
        rename_all_action.triggered.connect(self.rename_all_files)
        file_actions_menu.addAction(rename_all_action)
        
        file_actions_menu.addSeparator()
        
        reencode_action = QAction("Re-encode FLAC (Selected)", self)
        reencode_action.triggered.connect(self.reencode_flac_selected)
        file_actions_menu.addAction(reencode_action)
        
        reencode_all_action = QAction("Re-encode FLAC (All Visible)", self)
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
        
        hints_action = QAction("Hints && Tips", self)
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
        get_covers_action = QAction("Get Covers (Selected)", self)
        # fetch_all_covers checks selection if global mode, but we might need to force it
        # Actually fetch_all_covers checks sidebar.is_global_mode. 
        # We should probably make a helper that respects selection regardless of mode for context menu.
        # But wait, the user said "when i right click a single song make get covers (selected) appears which should also work when i select all of them"
        # So context menu should always act on selection.
        
        # Let's create specific lambdas or methods for context menu that force using selection
        get_covers_action.triggered.connect(self.fetch_covers_context)
        get_covers_action.setEnabled(has_selection)
        menu.addAction(get_covers_action)
        
        resize_covers_action = QAction("Resize Covers (Selected)", self)
        resize_covers_action.triggered.connect(self.resize_selected_covers)
        resize_covers_action.setEnabled(has_selection)
        menu.addAction(resize_covers_action)
        
        menu.addSeparator()
        
        # Lyrics
        get_lyrics_action = QAction("Get Lyrics (Selected)", self)
        get_lyrics_action.triggered.connect(self.fetch_lyrics_context)
        get_lyrics_action.setEnabled(has_selection)
        menu.addAction(get_lyrics_action)
        
        romanize_action = QAction("Romanize Lyrics (Selected)", self)
        romanize_action.triggered.connect(self.romanize_context)
        romanize_action.setEnabled(has_selection)
        menu.addAction(romanize_action)
        
        menu.addSeparator()
        
        # File Actions
        rename_action = QAction("Rename Files (Selected)", self)
        rename_action.triggered.connect(self.rename_selected_files)
        rename_action.setEnabled(has_selection)
        menu.addAction(rename_action)
        
        reencode_action = QAction("Re-encode FLAC (Selected)", self)
        reencode_action.triggered.connect(self.reencode_flac_selected)
        reencode_action.setEnabled(has_selection)
        menu.addAction(reencode_action)
        
        menu.addSeparator()
        
        autotag_action = QAction("Auto-Tag (Selected)", self)
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
            self.show_toast("No files are currently visible to edit.")
        else:
            # Force update if needed, but selection change should trigger it
            pass



    def exit_global_mode(self):
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
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
            
        if not self._prepare_batch("Get Lyrics Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setFormat("Processing... 0%")
        
        self._start_batch_worker(LyricsWorker(files, self.lyrics_fetcher), connect_log=True)

    def on_batch_progress(self, current, total):
        self.progress_bar.setValue(current)
        self.batch_dialog.update_progress(current, total)
        percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setFormat(f"Processing... {percent}%")
        
    def on_batch_result(self, filepath, status, message):
        self.batch_dialog.add_result(filepath, status, message)
        if status in ["Updated", "Success", "Found"]:
            self.file_list.update_file(filepath)
        
    def on_batch_log(self, message):
        print(message)
    
    def cancel_batch_operation(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
        # We don't set batch_running = False here; 
        # it will be set in on_batch_finished when the thread actually stops.
        self.batch_container.setVisible(False)
        self.batch_cancel_btn.setVisible(False)
        self._persistent_toast = None
        self.show_toast("Operation canceled", duration=3000)
        
    def on_batch_finished(self):
        self.batch_running = False
        self.batch_dialog.set_finished()
        # self.batch_container.setVisible(False) # Keep visible for persistence
        self.batch_cancel_btn.setVisible(False)
        self.progress_bar.setFormat("Finished (Click for details)")
        self.progress_bar.setValue(self.progress_bar.maximum())
        
        # Generate detailed summary
        results = self.batch_dialog.results
        total = len(results)
        
        if total == 0:
            self.show_toast("Done (No files processed)", is_batch=True)
            return

        success_count = len([r for r in results if r['status'] in ['Success', 'Updated', 'Found', 'Renamed']])
        skipped_count = len([r for r in results if r['status'] == 'Skipped'])
        error_count = len([r for r in results if r['status'] in ['Error', 'Missing', 'Failed']])
        
        if skipped_count == total:
            msg = f"Skipped, {total} files already up to date."
        elif success_count == total:
            msg = f"Done, updated {total} files."
        elif error_count == total:
            msg = f"Failed, {total} errors occurred."
        else:
            parts = []
            if success_count > 0: parts.append(f"Updated {success_count}")
            if skipped_count > 0: parts.append(f"Skipped {skipped_count}")
            if error_count > 0: parts.append(f"Failed {error_count}")
            msg = "Done. " + ", ".join(parts)
            
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
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
            
        if not self._prepare_batch("Get Covers Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setFormat("Processing... 0%")
        
        self._start_batch_worker(CoverFetchWorker(files, self.cover_manager))

    def resize_selected_covers(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Please select files.")
            return
        self._resize_covers(files)

    def resize_all_covers(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
        self._resize_covers(files)

    def _resize_covers(self, files):
        if not self._prepare_batch("Resize Covers Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setFormat("Resizing... 0%")
        
        self._start_batch_worker(CoverResizeWorker(files))

    def romanize_all(self):
        files = self.get_all_files()
        self._romanize_list(files)

    def _romanize_list(self, files):
        available, msg = DependencyChecker.check_koroman()
        if not available:
            dialogs.show_error(self, "Missing Dependency", msg)
            return
        
        if not files:
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
            
        if not self._prepare_batch("Romanize Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setFormat("Romanizing... 0%")
        
        self._start_batch_worker(RomanizeWorker(files, self.romanizer))

    def open_rename_dialog(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Please select files to rename.")
            return
        self._show_rename_dialog(files)

    def rename_selected_files(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Please select files to rename.")
            return
        self._show_rename_dialog(files)

    def rename_all_files(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "No files loaded.")
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
            self.progress_bar.setRange(0, len(rename_data))
            self.progress_bar.setFormat("Renaming... 0%")
            
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
            dialogs.show_warning(self, "No Selection", "Please select files.")
            return
            
        if not self._prepare_batch("Case Conversion Status"):
            return
            
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setFormat("Converting... 0%")
        
        self._start_batch_worker(CaseConvertWorker(files, mode))

    def reencode_flac_selected(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Selection", "Please select files to re-encode.")
            return
        self._reencode_flac_files(files)

    def reencode_flac_all(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
        self._reencode_flac_files(files)

    def _reencode_flac_files(self, files):
        available, msg = DependencyChecker.check_flac_tools()
        if not available:
            dialogs.show_error(self, "Missing Dependency", msg)
            return
        
        flac_files = [f for f in files if f.lower().endswith('.flac')]
        if not flac_files:
            dialogs.show_warning(self, "No FLAC Files", "No FLAC files in selection.")
            return
        
        if not self._prepare_batch("Re-encode FLAC Status"):
            return
            
        self.progress_bar.setRange(0, len(flac_files))
        self.progress_bar.setFormat("Re-encoding... 0%")
        
        self._start_batch_worker(FlacReencodeWorker(flac_files))

    def export_to_csv(self):
        files = self.file_list.all_files
        if not files:
            dialogs.show_warning(self, "No Files", "No files to export.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Metadata", "", "CSV Files (*.csv)")
        if not filepath:
            return
        
        from tagqt.core.csv_io import export_metadata_to_csv
        success, error = export_metadata_to_csv(files, filepath)
        if success:
            self.show_toast(f"Exported {len(files)} files to CSV")
        else:
            dialogs.show_warning(self, "Export Failed", error)

    def import_from_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Metadata", "", "CSV Files (*.csv)")
        if not filepath:
            return
        
        from tagqt.core.csv_io import import_metadata_from_csv
        rows, error = import_metadata_from_csv(filepath)
        if error:
            dialogs.show_warning(self, "Import Failed", error)
            return
        
        if not self._prepare_batch("CSV Import Status"):
            return
            
        self.progress_bar.setRange(0, len(rows))
        self.progress_bar.setFormat("Importing... 0%")
        
        self._start_batch_worker(CsvImportWorker(rows))

    def autotag_selected(self):
        files = self.get_selected_files()
        if not files:
            dialogs.show_warning(self, "No Files", "No files selected.")
            return
        self._autotag_files(files)
    
    def autotag_all(self):
        files = self.get_all_files()
        if not files:
            dialogs.show_warning(self, "No Files", "No files loaded.")
            return
        self._autotag_files(files)
    
    def _autotag_files(self, files):
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Auto-Tag Options")
        msg.setText(f"Auto-tag {len(files)} files from MusicBrainz?")
        msg.setInformativeText("Choose how to handle files that already have tags:")
        
        skip_btn = msg.addButton("Skip Tagged Files", QMessageBox.AcceptRole)
        all_btn = msg.addButton("Process All Files", QMessageBox.ActionRole)
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
        self.progress_bar.setFormat("Auto-tagging... 0%")
        
        self._start_batch_worker(AutoTagWorker(files, skip_existing=skip_existing), connect_log=True)

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder_path:
            self.load_folder(folder_path)

    def load_folder(self, folder_path):
        if not self._prepare_batch("Loading Folder"):
            return
            
        self.progress_bar.setFormat("Scanning folder...")
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
            self.show_toast(f"Loaded {len(results)} files from {os.path.basename(folder_path)}", is_batch=True)
        else:
             self.show_toast(f"No audio files found in {os.path.basename(folder_path)}", is_batch=False)

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
        self.setStyleSheet(Theme.get_stylesheet())
        self.sidebar.setStyleSheet(Theme.get_stylesheet())

    def show_hints(self):
        hints_text = """<h3>Usage Tips</h3>
<p><b>Batch Operations</b></p>
<ul>
<li>Click the progress bar to view details</li>
<li>Use the × button to cancel any operation</li>
</ul>

<p><b>Editing</b></p>
<ul>
<li>Global Edit applies changes to all visible files at once</li>
<li>Right-click column headers to show/hide columns</li>
</ul>

<p><b>Dependencies</b></p>
<ul>
<li><b>Romanize</b>: pip install koroman</li>
<li><b>Re-encode FLAC</b>: ffmpeg (apt install ffmpeg)</li>
<li><b>Auto-Tag</b>: pip install musicbrainzngs</li>
</ul>

<p><b>Supported Formats</b>: MP3, FLAC, OGG, M4A, WAV</p>
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.set_content(hints_text)
        dialog.exec()
    
    def show_shortcuts(self):
        shortcuts_text = """<h3>Keyboard Shortcuts</h3>
<table cellpadding="8">
<tr><td><b>Ctrl+O</b></td><td>Open folder</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save metadata</td></tr>
<tr><td><b>Ctrl+G</b></td><td>Global edit mode</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit application</td></tr>
<tr><td><b>Escape</b></td><td>Exit global edit mode</td></tr>
</table>
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.set_content(shortcuts_text)
        dialog.exec()
    
    def show_about(self):
        about_text = """<h2 style="margin-bottom: 5px;">TagQt</h2>
<p style="color: #666; margin-top: 0;">Music Metadata Editor</p>

<p>A modern application for editing audio file metadata, built with PySide6.</p>

<p><b>Capabilities</b></p>
<ul>
<li>Edit tags for MP3, FLAC, OGG, M4A, WAV</li>
<li>Auto-tag using MusicBrainz database</li>
<li>Fetch lyrics and album artwork</li>
<li>Batch rename and re-encode files</li>
</ul>
"""
        from tagqt.ui.help import HelpDialog
        dialog = HelpDialog(self)
        dialog.set_content(about_text)
        dialog.exec()

    def change_display_mode(self, mode):
        self.file_list.set_display_mode(mode)

    def on_file_selected(self, item, column):
        # Handle both top-level items (files in File mode) and children (files in Group mode)
        # Prevent loading if we are in multi-select mode (Global Edit)
        if len(self.file_list.selectedItems()) > 1:
            return

        # Groups don't have file paths in user role usually, or we need to check.
        filepath = item.data(0, Qt.UserRole)
        if filepath:
            self.load_file(filepath)
        else:
            # It's a group header
            pass

    def on_files_dropped(self, files):
        if files:
            for f in files:
                self.file_list.add_file(f)
            # Load the first one
            self.load_file(files[0])

    def on_selection_changed(self):
        files = self.get_selected_files()
        if len(files) > 1:
            self.sidebar.set_global_mode(True)
            self.current_file = None # Clear current single file context
            self.metadata = None
        elif len(files) == 1:
            self.sidebar.set_global_mode(False)
            self.load_file(files[0])
        else:
            self.sidebar.set_global_mode(False)
            # Clear sidebar?
            
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
                self.show_toast("No fields were modified.")
                return
                
            if not self._prepare_batch("Global Save Status"):
                return
            self.progress_bar.setRange(0, len(files))
            self.progress_bar.setFormat("Saving... 0%")
            
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
                
            self.show_toast("Changes saved")
            
            # Refresh the item in the list
            self.file_list.update_file(self.current_file)

    def romanize_metadata(self):
        if getattr(self.sidebar, 'is_global_mode', False):
            # Process strictly selected files in global mode
            files = self.get_selected_files()
            if files:
                self._romanize_list(files)
            else:
                dialogs.show_warning(self, "No Selection", "Please select files to romanize.")
            return
            
        available, msg = DependencyChecker.check_koroman()
        if not available:
            dialogs.show_error(self, "Missing Dependency", msg)
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
                self.show_toast("Lyrics loaded into editor. Don't forget to save!")
            else:
                dialogs.show_warning(self, "Empty", "Selected result has no lyrics text.")

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
                dialogs.show_error(self, "Error", f"Error downloading cover: {e}")

    def load_cover_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cover Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
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
                    dialogs.show_warning(self, "Invalid Image", "The selected file is not a valid image.")
            except Exception as e:
                dialogs.show_error(self, "Error", f"Error loading cover: {e}")

    def load_lyrics_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Lyrics File", "", "Lyrics (*.lrc *.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lyrics = f.read()
                
                self.sidebar.lyrics_edit.setText(lyrics)
            except Exception as e:
                dialogs.show_error(self, "Error", f"Error loading lyrics: {e}")
