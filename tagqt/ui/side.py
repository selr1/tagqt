from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QLabel, QHBoxLayout, QScrollArea, QFrame,
    QBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from tagqt.ui.theme import Theme

class ClickableLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class Sidebar(QWidget):
    save_clicked = Signal()
    romanize_clicked = Signal()
    lyrics_clicked = Signal()
    cover_clicked = Signal()
    load_cover_clicked = Signal()
    load_lyrics_clicked = Signal()
    cancel_global_clicked = Signal()
    reencode_flac_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self._current_res = ""
        self._current_specs = ""
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;") # Match parent bg
        
        # Container for scroll content
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 10, 0) # Right margin for scrollbar
        layout.setSpacing(20)
        
        scroll.setWidget(content_widget)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        main_layout.addWidget(scroll)

        # Cover Art
        self.cover_label = ClickableLabel()
        self.cover_label.clicked.connect(self.cover_clicked.emit)
        self.cover_label.setCursor(Qt.PointingHandCursor)
        self.cover_label.setFixedSize(200, 200)
        self.cover_label.setStyleSheet(f"background-color: {Theme.SURFACE0}; border-radius: {Theme.CORNER_RADIUS};")
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setText("No Cover")
        
        cover_container = QHBoxLayout()
        cover_container.addStretch()
        cover_container.addWidget(self.cover_label)
        cover_container.addStretch()
        layout.addLayout(cover_container)
        
        # Resolution Label
        self.resolution_label = QLabel("")
        self.resolution_label.setAlignment(Qt.AlignCenter)
        self.resolution_label.setStyleSheet(f"color: {Theme.SUBTEXT0}; font-size: 12px;")
        layout.addWidget(self.resolution_label)

        # Metadata Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.title_edit = QLineEdit()
        self.artist_edit = QLineEdit()
        self.album_edit = QLineEdit()
        self.album_artist_edit = QLineEdit()
        
        self.title_label = QLabel("Title:")
        form_layout.addRow(self.title_label, self.title_edit)
        form_layout.addRow("Artist:", self.artist_edit)
        form_layout.addRow("Album:", self.album_edit)
        form_layout.addRow("Album Artist:", self.album_artist_edit)
        
        self.year_edit = QLineEdit()
        self.genre_edit = QLineEdit()
        form_layout.addRow("Year:", self.year_edit)
        form_layout.addRow("Genre:", self.genre_edit)
        
        layout.addLayout(form_layout)
        
        # Collapsible Extended Metadata
        self.toggle_btn = QPushButton("Show More")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet(f"background-color: {Theme.SURFACE0}; color: {Theme.SUBTEXT0}; text-align: left; padding: 8px;")
        self.toggle_btn.clicked.connect(self.toggle_extended)
        layout.addWidget(self.toggle_btn)
        
        self.extended_widget = QWidget()
        self.extended_widget.setVisible(False)
        extended_layout = QFormLayout(self.extended_widget)
        extended_layout.setContentsMargins(0, 0, 0, 0)
        extended_layout.setSpacing(15)
        
        self.disc_edit = QLineEdit()
        self.track_edit = QLineEdit()
        self.bpm_edit = QLineEdit()
        self.key_edit = QLineEdit()
        self.isrc_edit = QLineEdit()
        self.publisher_edit = QLineEdit()
        self.comment_edit = QLineEdit()
        
        self.disc_label = QLabel("Disc:")
        extended_layout.addRow(self.disc_label, self.disc_edit)
        self.track_label = QLabel("Track:")
        extended_layout.addRow(self.track_label, self.track_edit)
        self.bpm_label = QLabel("BPM:")
        extended_layout.addRow(self.bpm_label, self.bpm_edit)
        self.key_label = QLabel("Key:")
        extended_layout.addRow(self.key_label, self.key_edit)
        self.isrc_label = QLabel("ISRC:")
        extended_layout.addRow(self.isrc_label, self.isrc_edit)
        extended_layout.addRow("Label:", self.publisher_edit)
        extended_layout.addRow("Comment:", self.comment_edit)
        
        layout.addWidget(self.extended_widget)
        
        # Lyrics Editor
        self.lyrics_label = QLabel("Lyrics")
        self.lyrics_label.setStyleSheet(f"font-weight: bold; color: {Theme.SUBTEXT0}; margin-top: 10px;")
        layout.addWidget(self.lyrics_label)
        
        from PySide6.QtWidgets import QTextEdit
        self.lyrics_edit = QTextEdit()
        self.lyrics_edit.setPlaceholderText("Lyrics will appear here...")
        self.lyrics_edit.setMinimumHeight(150) # Ensure it has height
        self.lyrics_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: {Theme.CORNER_RADIUS};
                padding: 10px;
                font-family: '{Theme.FONT_FAMILY}', monospace;
            }}
            QTextEdit:focus {{
                border: 1px solid {Theme.ACCENT};
            }}
        """)
        layout.addWidget(self.lyrics_edit)

        # Specific Action Buttons (Inside Scroll)
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(12)

        # Romanize and Re-encode Buttons Row
        self.romanize_layout = QBoxLayout(QBoxLayout.LeftToRight)
        
        self.romanize_btn = QPushButton("Romanize Lyrics")
        self.romanize_btn.setProperty("class", "secondary")
        self.romanize_btn.setCursor(Qt.PointingHandCursor)
        self.romanize_btn.clicked.connect(self.romanize_clicked.emit)
        self.romanize_layout.addWidget(self.romanize_btn)
        
        self.reencode_btn = QPushButton("Re-encode FLAC")
        self.reencode_btn.setProperty("class", "secondary")
        self.reencode_btn.setCursor(Qt.PointingHandCursor)
        self.reencode_btn.clicked.connect(self.reencode_flac_clicked.emit)
        # Always visible or controlled by logic, but user requested it for single edit too
        self.reencode_btn.setVisible(True) 
        self.romanize_layout.addWidget(self.reencode_btn)
        
        actions_layout.addLayout(self.romanize_layout)

        # Lyrics Buttons Row
        lyrics_btn_layout = QHBoxLayout()
        self.lyrics_btn = QPushButton("Get Lyrics")
        self.lyrics_btn.setProperty("class", "secondary")
        self.lyrics_btn.setCursor(Qt.PointingHandCursor)
        self.lyrics_btn.clicked.connect(self.lyrics_clicked.emit)
        lyrics_btn_layout.addWidget(self.lyrics_btn)
        
        self.load_lyrics_btn = QPushButton("Load Lyrics")
        self.load_lyrics_btn.setProperty("class", "secondary")
        self.load_lyrics_btn.setCursor(Qt.PointingHandCursor)
        self.load_lyrics_btn.clicked.connect(self.load_lyrics_clicked.emit)
        lyrics_btn_layout.addWidget(self.load_lyrics_btn)
        actions_layout.addLayout(lyrics_btn_layout)

        # Cover Buttons Row
        cover_btn_layout = QHBoxLayout()
        self.cover_btn = QPushButton("Get Cover")
        self.cover_btn.setProperty("class", "secondary")
        self.cover_btn.setCursor(Qt.PointingHandCursor)
        self.cover_btn.clicked.connect(self.cover_clicked.emit)
        cover_btn_layout.addWidget(self.cover_btn)
        
        self.load_cover_btn = QPushButton("Load Cover")
        self.load_cover_btn.setProperty("class", "secondary")
        self.load_cover_btn.setCursor(Qt.PointingHandCursor)
        self.load_cover_btn.clicked.connect(self.load_cover_clicked.emit)
        cover_btn_layout.addWidget(self.load_cover_btn)
        actions_layout.addLayout(cover_btn_layout)

        layout.addLayout(actions_layout)
        layout.addStretch()

        # Fixed Bottom Buttons (Outside Scroll)
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(10)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {Theme.SURFACE1};")
        bottom_layout.addWidget(line)

        self.cancel_global_btn = QPushButton("Cancel Batch Edit")
        self.cancel_global_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_global_btn.clicked.connect(self.cancel_global_clicked.emit)
        self.cancel_global_btn.setVisible(False)
        self.cancel_global_btn.setStyleSheet(f"background-color: {Theme.SURFACE2}; color: {Theme.TEXT};")
        bottom_layout.addWidget(self.cancel_global_btn)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_clicked.emit)
        bottom_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(bottom_layout)

    def toggle_extended(self, checked):
        self.extended_widget.setVisible(checked)
        self.toggle_btn.setText("Hide" if checked else "Show More")

    def set_cover(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.cover_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.cover_label.setText("")
            self._current_res = f"{pixmap.width()}x{pixmap.height()}"
        else:
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("No Cover")
            self._current_res = ""
            
        self._update_info_label()

    def set_file_specs(self, specs):
        """
        specs: dict with keys 'bitrate', 'sample_rate', 'filesize'
        """
        if not specs:
            self._current_specs = ""
        else:
            self._current_specs = f"{specs.get('bitrate', 0)}kbps | {specs.get('sample_rate', 0)}kHz | {specs.get('filesize', 0)}MB"
        self._update_info_label()

    def _update_info_label(self):
        parts = []
        if self._current_res:
            parts.append(self._current_res)
        if self._current_specs:
            parts.append(self._current_specs)
        
        if parts:
            self.resolution_label.setText(" • ".join(parts))
        else:
            self.resolution_label.setText("")

    def set_global_mode(self, enabled):
        """
        Toggles Global Edit Mode.
        If enabled:
        - Hides fields that shouldn't be bulk edited (Title, Track, Lyrics, etc.)
        - Hides Load buttons but keeps Get buttons.
        - Shows placeholder cover art.
        """
        self.is_global_mode = enabled
        
        # Unique fields to hide entirely (with their labels)
        unique_widgets = [
            (self.title_label, self.title_edit),
            (self.disc_label, self.disc_edit),
            (self.track_label, self.track_edit),
            (self.bpm_label, self.bpm_edit),
            (self.key_label, self.key_edit),
            (self.isrc_label, self.isrc_edit),
        ]
        
        for label, widget in unique_widgets:
            label.setVisible(not enabled)
            widget.setVisible(not enabled)
            widget.setEnabled(not enabled)
        
        # Lyrics section - hide entirely in global mode
        self.lyrics_label.setVisible(not enabled)
        self.lyrics_edit.setVisible(not enabled)
        
        # Load buttons - hide in global mode (loading from file doesn't make sense for batch)
        self.load_lyrics_btn.setVisible(not enabled)
        self.load_cover_btn.setVisible(not enabled)

        # Common fields: Artist, Album, Album Artist, Year, Genre, Comment, Publisher
        common_fields = [
            self.artist_edit,
            self.album_edit,
            self.album_artist_edit,
            self.year_edit,
            self.genre_edit,
            self.disc_edit,
            self.comment_edit,
            self.publisher_edit
        ]
        
        if enabled:
            for w in common_fields:
                w.setText("")
                w.setPlaceholderText("<Keep Original>")
            
            self.save_btn.setText("Save All Changes")
            self.cancel_global_btn.setVisible(True)
            # self.reencode_btn.setVisible(True) # Now shared
            
            # Button labels stay the same in global mode - it's already implied
            self.lyrics_btn.setText("Get Lyrics")
            self.cover_btn.setText("Get Cover")
            self.romanize_btn.setText("Romanize Lyrics")
            
            # Cover
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("Get Cover")
            
            self._current_res = ""
            self._current_specs = "Multiple Files Selected"
            self._update_info_label()
            
            self.setStyleSheet(f"#Sidebar {{ background-color: {Theme.MANTLE}; }}")
            
            # Stack buttons vertically in Global Mode
            self.romanize_layout.setDirection(QBoxLayout.TopToBottom)
            
        else:
            for w in common_fields:
                w.setPlaceholderText("")
            
            self.save_btn.setText("Save Changes")
            self.cancel_global_btn.setVisible(False)
            # self.reencode_btn.setVisible(False) # Support single edit
            
            # Restore original button labels
            self.lyrics_btn.setText("Get Lyrics")
            self.cover_btn.setText("Get Cover")
            self.romanize_btn.setText("Romanize Lyrics")
            
            self.setStyleSheet("")
            
            # Side-by-side in Single Mode
            self.romanize_layout.setDirection(QBoxLayout.LeftToRight)

    def get_modified_fields(self):
        """
        Returns a dictionary of fields that have been modified in Global Mode.
        Only returns fields that have non-empty text (overriding the placeholder).
        """
        changes = {}
        
        if not hasattr(self, 'is_global_mode') or not self.is_global_mode:
            return changes

        # Map widgets to metadata keys
        field_map = {
            self.artist_edit: 'artist',
            self.album_edit: 'album',
            self.album_artist_edit: 'album_artist',
            self.year_edit: 'year',
            self.genre_edit: 'genre',
            self.disc_edit: 'disc_number',
            self.track_edit: 'track_number',
            self.publisher_edit: 'publisher',
            self.comment_edit: 'comment'
        }
        
        for widget, key in field_map.items():
            text = widget.text().strip()
            if text and text != "<Keep Original>":
                changes[key] = text
                
        return changes

