from PySide6.QtWidgets import QMessageBox, QProgressDialog
from PySide6.QtCore import Qt
from tagqt.ui.theme import Theme


def show_info(parent, title, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(Theme.current_stylesheet())
    msg.exec()


def show_warning(parent, title, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(Theme.current_stylesheet())
    msg.exec()


def show_error(parent, title, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(Theme.current_stylesheet())
    msg.exec()


def show_question(parent, title, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setStyleSheet(Theme.current_stylesheet())
    return msg.exec() == QMessageBox.Yes


def create_progress(parent, title, message, max_value):
    progress = QProgressDialog(message, "Cancel", 0, max_value, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModal)
    progress.setStyleSheet(Theme.current_stylesheet())
    return progress
