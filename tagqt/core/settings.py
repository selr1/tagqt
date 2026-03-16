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
    
    def get_flavor(self):
        return self.settings.value("theme_flavor", "mocha")
    
    def set_flavor(self, flavor):
        self.settings.setValue("theme_flavor", flavor)
    
    def get_lyrics_providers(self) -> list[str]:
        """
        Return the list of enabled provider keys in user-defined order.
        Defaults to all three enabled.
        """
        default = ["syncedlyrics_word", "syncedlyrics_line", "lrclib"]
        val = self.settings.value("lyrics_providers", default)
        # QSettings may deserialize as a single string if only one item was saved
        if isinstance(val, str):
            val = [val]
        return val if val else default

    def set_lyrics_providers(self, providers: list[str]):
        self.settings.setValue("lyrics_providers", providers)

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

