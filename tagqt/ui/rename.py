from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from tagqt.ui.theme import Theme
from tagqt.core.rename import Renamer
import os

class RenamerDialog(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QApplication
        self.setWindowIcon(QApplication.instance().windowIcon())
        self.setWindowTitle("Rename Files")
        self.resize(600, 500)
        self.setStyleSheet(Theme.current_stylesheet())
        
        self.files = files # List of (filepath, metadata) tuples
        self.preview_data = {} # filepath -> new_name
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Pattern Input
        pattern_layout = QFormLayout()
        self.pattern_edit = QLineEdit("%artist% - %title%")
        self.pattern_edit.textChanged.connect(self.update_preview)
        pattern_layout.addRow("Pattern", self.pattern_edit)
        layout.addLayout(pattern_layout)
        
        # Help Label
        help_label = QLabel("Tags you can use: %artist%, %title%, %album%, %year%, %track%, %genre%, %bpm%, %key%")
        help_label.setStyleSheet(f"color: {Theme.SUBTEXT0}; font-size: 12px;")
        layout.addWidget(help_label)
        
        # Preview List
        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Rename")
        ok_btn.setProperty("class", "primary")
        ok_btn.setCursor(Qt.PointingHandCursor)
        
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(buttons)
        
        self.update_preview()

    def update_preview(self):
        self.preview_list.clear()
        self.preview_data = {}
        pattern = self.pattern_edit.text()
        
        for filepath, metadata in self.files:
            if not metadata:
                continue
                
            new_filename = Renamer.tag_to_filename(pattern, metadata)
            if new_filename:
                # Append extension
                ext = os.path.splitext(filepath)[1]
                new_filename += ext
                
                self.preview_data[filepath] = new_filename
                
                item = QListWidgetItem(f"{os.path.basename(filepath)}  ->  {new_filename}")
                self.preview_list.addItem(item)
