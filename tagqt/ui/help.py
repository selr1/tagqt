from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextBrowser, QPushButton, 
    QHBoxLayout
)
from PySide6.QtCore import Qt
from tagqt.ui.theme import Theme

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 400)
        self.setStyleSheet(Theme.get_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Content
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {Theme.SURFACE0};
                border: 1px solid {Theme.SURFACE1};
                border-radius: {Theme.CORNER_RADIUS};
                padding: 15px;
                color: {Theme.TEXT};
            }}
        """)
        layout.addWidget(self.browser)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setProperty("class", "primary")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setFixedWidth(100)
        
        footer_layout.addWidget(self.close_btn)
        layout.addLayout(footer_layout)

    def set_content(self, html_content):
        # Inject some CSS for better HTML rendering inside the browser
        styled_html = f"""
        <style>
            h3 {{ color: {Theme.ACCENT}; margin-top: 20px; margin-bottom: 10px; }}
            ul {{ margin-left: 20px; }}
            li {{ margin-bottom: 8px; color: {Theme.SUBTEXT1}; }}
            b {{ color: {Theme.TEXT}; }}
            code {{ background-color: {Theme.SURFACE1}; padding: 2px 4px; border-radius: 3px; }}
        </style>
        {html_content}
        """
        self.browser.setHtml(styled_html)
