from PySide6.QtCore import QSettings


class Settings:
    """Manages persistent application settings using QSettings."""
    
    def __init__(self):
        self.settings = QSettings("TagQt", "TagQt")
    
    def get_recent_folders(self):
        folders = self.settings.value("recent_folders", [])
        if isinstance(folders, str):
            return [folders] if folders else []
        return folders or []
    
    def add_recent_folder(self, folder):
        folders = self.get_recent_folders()
        if folder in folders:
            folders.remove(folder)
        folders.insert(0, folder)
        folders = folders[:10]
        self.settings.setValue("recent_folders", folders)
    
    def clear_recent_folders(self):
        self.settings.setValue("recent_folders", [])
    
    def get_light_theme(self):
        return self.settings.value("light_theme", False, type=bool)
    
    def set_light_theme(self, enabled):
        self.settings.setValue("light_theme", enabled)
    
    def get_hidden_columns(self):
        cols = self.settings.value("hidden_columns", [])
        if isinstance(cols, str):
            return [int(cols)] if cols else []
        return [int(c) for c in cols] if cols else []
    
    def set_hidden_columns(self, columns):
        self.settings.setValue("hidden_columns", columns)

    def get_last_folder(self):
        return self.settings.value("last_folder", "")

    def set_last_folder(self, folder):
        self.settings.setValue("last_folder", folder)

