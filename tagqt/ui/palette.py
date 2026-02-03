from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from tagqt.ui.theme import Theme


class CommandPalette(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.SURFACE0};
                border: 1px solid {Theme.SURFACE1};
                border-radius: {Theme.CORNER_RADIUS};
            }}
        """)
        
        self.commands = []
        self.filtered_commands = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a command...")
        self.input.textChanged.connect(self.on_filter)
        self.input.returnPressed.connect(self.execute_selected)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.MANTLE};
                border: none;
                border-radius: {Theme.CORNER_RADIUS};
                padding: 12px 15px;
                color: {Theme.TEXT};
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.input)
        
        self.list = QListWidget()
        self.list.setFocusPolicy(Qt.NoFocus)
        self.list.itemClicked.connect(self.on_item_clicked)
        self.list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 15px;
                border-radius: 4px;
                color: {Theme.TEXT};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.ACCENT};
                color: {Theme.CRUST};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.SURFACE1};
            }}
        """)
        self.list.setMaximumHeight(300)
        layout.addWidget(self.list)
        
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Up"), self, self.move_up)
        QShortcut(QKeySequence("Down"), self, self.move_down)
    
    def register_commands(self, commands):
        self.commands = commands
        self.refresh_list()
    
    def refresh_list(self, filter_text=""):
        self.list.clear()
        filter_text = filter_text.lower()
        self.filtered_commands = []
        
        for cmd in self.commands:
            name = cmd.get("name", "")
            shortcut = cmd.get("shortcut", "")
            if not filter_text or filter_text in name.lower():
                self.filtered_commands.append(cmd)
                item = QListWidgetItem(f"{name}  {shortcut}")
                item.setData(Qt.UserRole, cmd)
                self.list.addItem(item)
        
        if self.list.count() > 0:
            self.list.setCurrentRow(0)
    
    def on_filter(self, text):
        self.refresh_list(text)
    
    def move_up(self):
        row = self.list.currentRow()
        if row > 0:
            self.list.setCurrentRow(row - 1)
    
    def move_down(self):
        row = self.list.currentRow()
        if row < self.list.count() - 1:
            self.list.setCurrentRow(row + 1)
    
    def execute_selected(self):
        item = self.list.currentItem()
        if item:
            cmd = item.data(Qt.UserRole)
            callback = cmd.get("callback")
            self.close()
            if callback:
                callback()
    
    def on_item_clicked(self, item):
        cmd = item.data(Qt.UserRole)
        callback = cmd.get("callback")
        self.close()
        if callback:
            callback()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.input.clear()
        self.input.setFocus()
        self.refresh_list()
        
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + 100
            self.move(x, y)
