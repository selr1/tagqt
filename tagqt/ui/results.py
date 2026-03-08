from PySide6.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QLabel, QHeaderView
from PySide6.QtCore import Qt
from tagqt.ui.theme import Theme

class SearchResultsDialog(QDialog):
    def __init__(self, results, parent=None, mode="lyrics"):
        super().__init__(parent)
        from PySide6.QtWidgets import QApplication
        self.setWindowIcon(QApplication.instance().windowIcon())
        self.setWindowTitle(f"Select {mode.capitalize()}")
        self.resize(700, 450)
        self.setStyleSheet(Theme.get_stylesheet())
        
        self.selected_result = None
        self.mode = mode
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"Search Results ({mode.capitalize()})")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.ACCENT};")
        layout.addWidget(header)
        
        # Tree Widget
        self.tree = QTreeWidget()
        
        if mode == "lyrics":
            self.tree.setHeaderLabels(["Title", "Artist", "Album", "Duration", "Type"])
        else: # cover
            self.tree.setHeaderLabels(["Album", "Artist", "Source", "Size"])
            
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.setRootIsDecorated(False)
        self.tree.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.tree)
        
        # Populate
        for res in results:
            if mode == "lyrics":
                duration_str = self.format_duration(res.get("duration", 0))
                type_str = "Synced" if res.get("isSynced") else "Plain"
                
                item = QTreeWidgetItem([
                    res.get("trackName", ""),
                    res.get("artistName", ""),
                    res.get("albumName", ""),
                    duration_str,
                    type_str
                ])
            else: # cover
                item = QTreeWidgetItem([
                    res.get("album", ""),
                    res.get("artist", ""),
                    res.get("source", ""),
                    res.get("size", "")
                ])
            
            # Store full result in data
            item.setData(0, Qt.UserRole, res)
            self.tree.addTopLevelItem(item)
            
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Select")
        ok_btn.setProperty("class", "primary")
        ok_btn.setCursor(Qt.PointingHandCursor)
        
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(buttons)

    def format_duration(self, seconds):
        if not seconds:
            return ""
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def accept_selection(self):
        item = self.tree.currentItem()
        if item:
            self.selected_result = item.data(0, Qt.UserRole)
            self.accept()
