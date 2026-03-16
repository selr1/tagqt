"""
Catppuccin theme for TagQt — pixel-perfect VS Code aesthetic.

Single source of truth for ALL colors. No hex strings hardcoded elsewhere.
Supports four Catppuccin flavors: Latte, Frappé, Macchiato, Mocha.
"""


# ═══ Flavor palettes (static reference data) ═════════════════════
_PALETTES = {
    "mocha": {
        "ROSEWATER": "#f5e0dc", "FLAMINGO": "#f2cdcd", "PINK": "#f5c2e7",
        "MAUVE": "#cba6f7", "RED": "#f38ba8", "MAROON": "#eba0ac",
        "PEACH": "#fab387", "YELLOW": "#f9e2af", "GREEN": "#a6e3a1",
        "TEAL": "#94e2d5", "SKY": "#89dceb", "SAPPHIRE": "#74c7ec",
        "BLUE": "#89b4fa", "LAVENDER": "#b4befe",
        "TEXT": "#cdd6f4", "SUBTEXT1": "#bac2de", "SUBTEXT0": "#a6adc8",
        "OVERLAY2": "#7f849c", "OVERLAY1": "#6c7086", "OVERLAY0": "#585b70",
        "SURFACE2": "#585b70", "SURFACE1": "#45475a", "SURFACE0": "#313244",
        "BASE": "#1e1e2e", "MANTLE": "#181825", "CRUST": "#11111b",
        "ACCENT_HOVER": "#b597e8", "ACCENT_DIM": "#a688d9",
    },
    "macchiato": {
        "ROSEWATER": "#f4dbd6", "FLAMINGO": "#f0c6c6", "PINK": "#f5bde6",
        "MAUVE": "#c6a0f6", "RED": "#ed8796", "MAROON": "#ee99a0",
        "PEACH": "#f5a97f", "YELLOW": "#eed49f", "GREEN": "#a6da95",
        "TEAL": "#8bd5ca", "SKY": "#91d7e3", "SAPPHIRE": "#7dc4e4",
        "BLUE": "#8aadf4", "LAVENDER": "#b7bdf8",
        "TEXT": "#cad3f5", "SUBTEXT1": "#b8c0e0", "SUBTEXT0": "#a5adcb",
        "OVERLAY2": "#939ab7", "OVERLAY1": "#8087a2", "OVERLAY0": "#6e738d",
        "SURFACE2": "#5b6078", "SURFACE1": "#494d64", "SURFACE0": "#363a4f",
        "BASE": "#24273a", "MANTLE": "#1e2030", "CRUST": "#181926",
        "ACCENT_HOVER": "#b18ff0", "ACCENT_DIM": "#a07de0",
    },
    "frappe": {
        "ROSEWATER": "#f2d5cf", "FLAMINGO": "#eebebe", "PINK": "#f4b8e4",
        "MAUVE": "#ca9ee6", "RED": "#e78284", "MAROON": "#ea999c",
        "PEACH": "#ef9f76", "YELLOW": "#e5c890", "GREEN": "#a6d189",
        "TEAL": "#81c8be", "SKY": "#99d1db", "SAPPHIRE": "#85c1dc",
        "BLUE": "#8caaee", "LAVENDER": "#babbf1",
        "TEXT": "#c6d0f5", "SUBTEXT1": "#b5bfe2", "SUBTEXT0": "#a5adce",
        "OVERLAY2": "#949cbb", "OVERLAY1": "#838ba7", "OVERLAY0": "#737994",
        "SURFACE2": "#626880", "SURFACE1": "#51576d", "SURFACE0": "#414559",
        "BASE": "#303446", "MANTLE": "#292c3c", "CRUST": "#232634",
        "ACCENT_HOVER": "#b58ce0", "ACCENT_DIM": "#a47ad0",
    },
    "latte": {
        "ROSEWATER": "#dc8a78", "FLAMINGO": "#dd7878", "PINK": "#ea76cb",
        "MAUVE": "#8839ef", "RED": "#d20f39", "MAROON": "#e64553",
        "PEACH": "#fe640b", "YELLOW": "#df8e1d", "GREEN": "#40a02b",
        "TEAL": "#179299", "SKY": "#04a5e5", "SAPPHIRE": "#209fb5",
        "BLUE": "#1e66f0", "LAVENDER": "#7287fd",
        "TEXT": "#4c4f69", "SUBTEXT1": "#5c5f77", "SUBTEXT0": "#6c6f85",
        "OVERLAY2": "#7c7f93", "OVERLAY1": "#8c8fa1", "OVERLAY0": "#9ca0b0",
        "SURFACE2": "#acb0be", "SURFACE1": "#bcc0cc", "SURFACE0": "#ccd0da",
        "BASE": "#eff1f5", "MANTLE": "#e6e9ef", "CRUST": "#dce0e8",
        "ACCENT_HOVER": "#7730d6", "ACCENT_DIM": "#6627bd",
    },
}

FLAVORS = ("latte", "frappe", "macchiato", "mocha")
FLAVOR_LABELS = {"latte": "Latte", "frappe": "Frappé", "macchiato": "Macchiato", "mocha": "Mocha"}


class Theme:
    """Catppuccin color palette and Qt stylesheet generator."""

    _flavor = "mocha"


    CRUST    = "#11111b"
    MANTLE   = "#181825"
    BASE     = "#1e1e2e"
    SURFACE0 = "#313244"
    SURFACE1 = "#45475a"
    SURFACE2 = "#585b70"

    TEXT     = "#cdd6f4"
    SUBTEXT1 = "#bac2de"
    SUBTEXT0 = "#a6adc8"
    OVERLAY2 = "#7f849c"
    OVERLAY1 = "#6c7086"
    OVERLAY0 = "#585b70"


    ROSEWATER = "#f5e0dc"
    FLAMINGO  = "#f2cdcd"
    PINK      = "#f5c2e7"
    MAUVE     = "#cba6f7"
    RED       = "#f38ba8"
    MAROON    = "#eba0ac"
    PEACH     = "#fab387"
    YELLOW    = "#f9e2af"
    GREEN     = "#a6e3a1"
    TEAL      = "#94e2d5"
    SKY       = "#89dceb"
    SAPPHIRE  = "#74c7ec"
    BLUE      = "#89b4fa"
    LAVENDER  = "#b4befe"

    ACCENT       = MAUVE
    ACCENT_HOVER = "#b597e8"
    ACCENT_DIM   = "#a688d9"
    SUCCESS      = GREEN
    WARNING      = PEACH
    ERROR        = RED

    TOAST_TEXT   = CRUST
    WINDOW_BG    = BASE
    SIDEBAR_BG   = MANTLE
    BUTTON_TEXT  = TEXT

    FONT_FAMILY   = "JetBrains Mono"
    CORNER_RADIUS = "4px"

    @classmethod
    def set_flavor(cls, flavor: str):
        """Switch to any Catppuccin flavor (latte, frappe, macchiato, mocha)."""
        if flavor not in _PALETTES:
            flavor = "mocha"
        cls._flavor = flavor
        p = _PALETTES[flavor]
        for attr, val in p.items():
            setattr(cls, attr, val)
        cls.ACCENT       = cls.MAUVE
        cls.ACCENT_HOVER = p["ACCENT_HOVER"]
        cls.ACCENT_DIM   = p["ACCENT_DIM"]
        cls.SUCCESS      = cls.GREEN
        cls.WARNING      = cls.PEACH
        cls.ERROR        = cls.RED
        cls.TOAST_TEXT   = cls.BASE if cls.is_light() else cls.CRUST
        cls.WINDOW_BG    = cls.BASE
        cls.SIDEBAR_BG   = cls.MANTLE
        cls.BUTTON_TEXT  = "#ffffff" if cls.is_light() else cls.TEXT

    @classmethod
    def is_light(cls):
        return cls._flavor == "latte"

    @classmethod
    def get_palette(cls):
        from PySide6.QtGui import QPalette, QColor
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(cls.WINDOW_BG))
        palette.setColor(QPalette.WindowText, QColor(cls.TEXT))
        palette.setColor(QPalette.Base, QColor(cls.BASE))
        palette.setColor(QPalette.AlternateBase, QColor(cls.MANTLE))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.SURFACE0))
        palette.setColor(QPalette.ToolTipText, QColor(cls.TEXT))
        palette.setColor(QPalette.Text, QColor(cls.TEXT))
        palette.setColor(QPalette.Button, QColor(cls.SURFACE1))
        palette.setColor(QPalette.ButtonText, QColor(cls.BUTTON_TEXT))
        palette.setColor(QPalette.BrightText, QColor(cls.RED))
        palette.setColor(QPalette.Link, QColor(cls.BLUE))
        palette.setColor(QPalette.Highlight, QColor(cls.BLUE))
        palette.setColor(QPalette.HighlightedText, QColor(cls.BASE))
        return palette


    @staticmethod
    def get_stylesheet():
        return f"""
            /* ═══ Global ═══════════════════════════════ */

            QMainWindow {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
            }}
            QWidget {{
                font-family: '{Theme.FONT_FAMILY}', 'Cascadia Code', 'Consolas', monospace;
                color: {Theme.TEXT};
                font-size: 13px;
            }}
            QLabel {{
                color: {Theme.SUBTEXT0};
            }}

            /* ═══ Sidebar & Player Bar ═══════════════ */

            QWidget#Sidebar {{
                background-color: {Theme.MANTLE};
                border-left: 1px solid {Theme.SURFACE0};
            }}
            QWidget#playerBar {{
                background-color: {Theme.CRUST};
                border-top: 1px solid {Theme.SURFACE1};
            }}

            /* ═══ Inputs ══════════════════════════════ */

            QLineEdit {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 6px 10px;
                selection-background-color: rgba(137, 180, 250, 0.4);
                selection-color: {Theme.TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.ACCENT};
                background-color: {Theme.SURFACE0};
            }}
            QLineEdit:disabled {{
                color: {Theme.OVERLAY1};
                background-color: {Theme.SURFACE0};
            }}
            QTextEdit, QPlainTextEdit {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 6px 10px;
                selection-background-color: rgba(137, 180, 250, 0.4);
                selection-color: {Theme.TEXT};
            }}
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {Theme.ACCENT};
                background-color: {Theme.SURFACE0};
            }}

            /* ═══ Buttons ═════════════════════════════ */

            QPushButton {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: 400;
                font-size: 13px;
                min-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SURFACE1};
                border: 1px solid {Theme.SURFACE2};
            }}
            QPushButton:pressed {{
                background-color: {Theme.SURFACE2};
            }}
            QPushButton:focus {{
                border: 1px solid {Theme.MAUVE};
            }}
            QPushButton:disabled {{
                background-color: {Theme.SURFACE0};
                color: {Theme.OVERLAY1};
                border: 1px solid {Theme.SURFACE0};
            }}

            /* Primary */
            QPushButton[class="primary"] {{
                background-color: {Theme.MAUVE};
                color: {Theme.CRUST};
                border: none;
                font-weight: 600;
            }}
            QPushButton[class="primary"]:hover {{
                background-color: {Theme.ACCENT_HOVER};
            }}
            QPushButton[class="primary"]:pressed {{
                background-color: {Theme.ACCENT_DIM};
            }}
            QPushButton[class="primary"]:disabled {{
                background-color: {Theme.SURFACE0};
                color: {Theme.OVERLAY1};
            }}

            /* Destructive */
            QPushButton[class="destructive"] {{
                background-color: {Theme.RED};
                color: {Theme.CRUST};
                border: none;
            }}
            QPushButton[class="destructive"]:hover {{
                background-color: {Theme.MAROON};
            }}

            /* ═══ Combo Box ═══════════════════════════ */

            QComboBox {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 6px 10px;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border: 1px solid {Theme.MAUVE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.MANTLE};
                color: {Theme.TEXT};
                selection-background-color: {Theme.BLUE};
                selection-color: {Theme.CRUST};
                border: 1px solid {Theme.SURFACE1};
            }}

            /* ═══ Tree Widget (File List) ════════════ */

            QTreeWidget {{
                background-color: {Theme.BASE};
                alternate-background-color: {Theme.MANTLE};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 3px 6px;
                min-height: 22px;
                border-radius: 0px;
                color: {Theme.TEXT};
            }}
            QTreeWidget::item:alternate {{
                background-color: {Theme.MANTLE};
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
                border-left: 2px solid {Theme.MAUVE};
            }}
            QTreeWidget::item:hover {{
                background-color: {Theme.SURFACE0};
            }}
            QHeaderView::section {{
                background-color: {Theme.MANTLE};
                color: {Theme.SUBTEXT0};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {Theme.SURFACE1};
                font-weight: 600;
                font-size: 11px;
            }}

            /* ═══ Scroll ═════════════════════════════ */

            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(88, 91, 112, 0.6);
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.OVERLAY0};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {Theme.OVERLAY1};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: transparent;
                height: 10px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: rgba(88, 91, 112, 0.6);
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.OVERLAY0};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background: {Theme.OVERLAY1};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            /* ═══ Frames ═════════════════════════════ */

            QFrame {{
                border: none;
            }}

            /* ═══ Dialogs & Views ════════════════════ */

            QDialog {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
            }}
            QMessageBox {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
            }}
            QMessageBox QLabel {{
                color: {Theme.TEXT};
            }}
            QFileDialog {{
                background-color: {Theme.MANTLE};
                color: {Theme.TEXT};
            }}
            QInputDialog {{
                background-color: {Theme.BASE};
            }}

            QListView, QTreeView {{
                background-color: {Theme.BASE};
                alternate-background-color: {Theme.MANTLE};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                outline: none;
            }}
            QListView::item:selected, QTreeView::item:selected {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
            }}
            QListView::item:hover, QTreeView::item:hover {{
                background-color: {Theme.SURFACE0};
            }}

            /* ═══ Menus ══════════════════════════════ */

            QMenuBar {{
                background-color: {Theme.CRUST};
                color: {Theme.TEXT};
                border-bottom: 1px solid {Theme.SURFACE1};
                font-size: 13px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                color: {Theme.TEXT};
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
            }}
            QMenuBar::item:pressed {{
                background-color: {Theme.SURFACE1};
            }}
            QMenu {{
                background-color: {Theme.MANTLE};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
            }}
            QMenu::separator {{
                height: 1px;
                background: {Theme.SURFACE1};
                margin: 4px 8px;
            }}

            /* ═══ Progress ═══════════════════════════ */

            QProgressBar {{
                background-color: {Theme.SURFACE0};
                border: none;
                border-radius: 3px;
                text-align: center;
                color: {Theme.SUBTEXT1};
                height: 6px;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 3px;
            }}
            QProgressDialog {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
            }}

            /* ═══ Spin Box ═══════════════════════════ */

            QSpinBox, QDoubleSpinBox {{
                background-color: {Theme.SURFACE0};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                padding: 6px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Theme.MAUVE};
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {Theme.SURFACE1};
                border: none;
                width: 16px;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {Theme.SURFACE2};
            }}

            /* ═══ Slider ═════════════════════════════ */

            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: {Theme.SURFACE1};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {Theme.MAUVE};
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Theme.LAVENDER};
            }}

            /* ═══ Tabs ═══════════════════════════════ */

            QTabWidget::pane {{
                border: 1px solid {Theme.SURFACE1};
                background-color: {Theme.BASE};
                border-radius: 0px;
            }}
            QTabBar::tab {{
                background-color: {Theme.CRUST};
                color: {Theme.OVERLAY2};
                padding: 8px 16px;
                margin-right: 0px;
                border: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
            QTabBar::tab:selected {{
                background-color: {Theme.BASE};
                color: {Theme.TEXT};
                border-top: 1px solid {Theme.MAUVE};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {Theme.MANTLE};
            }}

            /* ═══ Checkbox & Radio ═══════════════════ */

            QCheckBox, QRadioButton {{
                color: {Theme.TEXT};
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {Theme.SURFACE0};
                border: 1px solid {Theme.SURFACE1};
            }}
            QCheckBox::indicator {{
                border-radius: 3px;
            }}
            QRadioButton::indicator {{
                border-radius: 8px;
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {Theme.BLUE};
                border-color: {Theme.BLUE};
            }}
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
                border-color: {Theme.MAUVE};
            }}
            QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
                background-color: {Theme.SURFACE0};
                border-color: {Theme.OVERLAY1};
            }}

            /* ═══ Group Box ══════════════════════════ */

            QGroupBox {{
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {Theme.SUBTEXT0};
                font-size: 11px;
            }}

            /* ═══ Tooltip ════════════════════════════ */

            QToolTip {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE2};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}

            /* ═══ Status Bar ═════════════════════════ */

            QStatusBar {{
                background-color: {Theme.CRUST};
                color: {Theme.SUBTEXT1};
                font-size: 11px;
            }}

            /* ═══ List Widget ════════════════════════ */

            QListWidget {{
                background-color: {Theme.BASE};
                alternate-background-color: {Theme.MANTLE};
                color: {Theme.TEXT};
                border: 1px solid {Theme.SURFACE1};
                border-radius: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 0px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.SURFACE1};
                color: {Theme.TEXT};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.SURFACE0};
            }}

            /* ═══ Dialog Button Box ══════════════════ */

            QDialogButtonBox {{
                button-layout: 3;
            }}
        """

    @classmethod
    def current_stylesheet(cls):
        return cls.get_stylesheet()
