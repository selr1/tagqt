import sys
from PySide6.QtWidgets import QApplication
from tagqt.ui.main import MainWindow
from tagqt.ui.theme import Theme

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Theme.get_stylesheet())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
