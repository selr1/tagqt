from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QProgressBar, QLabel, 
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from tagqt.ui.theme import Theme
from tagqt.ui.side import ClickableLabel
import os

class ClickableProgressBar(QProgressBar):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class BatchStatusDialog(QDialog):
    def __init__(self, parent=None, title="Batch Operation"):
        super().__init__(parent)
        from PySide6.QtWidgets import QApplication
        self.setWindowIcon(QApplication.instance().windowIcon())
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.setStyleSheet(Theme.current_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.status_label = QLabel("Starting\u2026")
        self.status_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.TEXT};")
        layout.addWidget(self.status_label)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {Theme.SURFACE0};
                height: 6px;
                min-height: 6px;
                max-height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Results Tree (Matching UnifiedSearchDialog style)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Status", "Details"])
        
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        
        layout.addWidget(self.tree)
        
        # Footer Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept) # Close acts as accept/reject here
        
        self.close_btn = buttons.button(QDialogButtonBox.Close)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setText("Close")
        
        layout.addWidget(buttons)
        
        self.results = [] 

    def update_progress(self, current, total):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        percent = int((current / total) * 100) if total > 0 else 0
        self.status_label.setText(f"{current} of {total} \u00b7 {percent}%")
    def set_finished(self):
        self.status_label.setText("All done.")
        self.progress_bar.setValue(self.progress_bar.maximum())

    def add_result(self, filepath, status, details):
        filename = os.path.basename(filepath)
        
        existing_item = None
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.text(0) == filename:
                existing_item = item
                break
        
        if existing_item:
            existing_item.setText(1, status)
            existing_item.setText(2, details)
            item = existing_item
        else:
            item = QTreeWidgetItem([filename, status, details])
            self.tree.addTopLevelItem(item)
        
        if status == "Success" or status == "Found" or status == "Updated":
            item.setForeground(1, QColor(Theme.SUCCESS))
        elif status == "Error" or status == "Missing":
            item.setForeground(1, QColor(Theme.RED))
        elif status == "Skipped":
            item.setForeground(1, QColor(Theme.SUBTEXT0))
        else:
            item.setForeground(1, QColor(Theme.SUBTEXT0))
        
        for i, r in enumerate(self.results):
            if r['file'] == filepath:
                self.results[i] = {'file': filepath, 'status': status, 'details': details}
                return
        self.results.append({'file': filepath, 'status': status, 'details': details})

    def clear(self):
        self.tree.clear()
        self.results = []
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
