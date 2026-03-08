"""
Catppuccin Mocha theme for TagQt — pixel-perfect VS Code aesthetic.

Single source of truth for ALL colors. No hex strings hardcoded elsewhere.
"""


class Theme:
    """Catppuccin Mocha color palette and Qt stylesheet generator."""

    _is_light = False


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

    # ═══ Catppuccin Latte (light) ════════════════
    LATTE_ROSEWATER = "#dc8a78"
    LATTE_FLAMINGO  = "#dd7878"
    LATTE_PINK      = "#ea76cb"
    LATTE_MAUVE     = "#8839ef"
    LATTE_RED       = "#d20f39"
    LATTE_MAROON    = "#e64553"
    LATTE_PEACH     = "#fe640b"
    LATTE_YELLOW    = "#df8e1d"
    LATTE_GREEN     = "#40a02b"
    LATTE_TEAL      = "#179299"
    LATTE_SKY       = "#04a5e5"
    LATTE_SAPPHIRE  = "#209fb5"
    LATTE_BLUE      = "#1e66f0"
    LATTE_LAVENDER  = "#7287fd"
    LATTE_TEXT      = "#4c4f69"
    LATTE_SUBTEXT1  = "#5c5f77"
    LATTE_SUBTEXT0  = "#6c6f85"
    LATTE_OVERLAY2  = "#7c7f93"
    LATTE_OVERLAY1  = "#8c8fa1"
    LATTE_OVERLAY0  = "#9ca0b0"
    LATTE_SURFACE2  = "#acb0be"
    LATTE_SURFACE1  = "#bcc0cc"
    LATTE_SURFACE0  = "#ccd0da"
    LATTE_BASE      = "#eff1f5"
    LATTE_MANTLE    = "#e6e9ef"
    LATTE_CRUST     = "#dce0e8"

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
    def set_light_mode(cls, enabled):
        """Toggle between Catppuccin Mocha (dark) and Latte (light)."""
        cls._is_light = enabled
        if enabled:
            # Catppuccin Latte
            cls.CRUST    = "#dce0e8"
            cls.MANTLE   = "#e6e9ef"
            cls.BASE     = "#eff1f5"
            cls.SURFACE0 = "#ccd0da"
            cls.SURFACE1 = "#bcc0cc"
            cls.SURFACE2 = "#acb0be"
            cls.TEXT      = "#4c4f69"
            cls.SUBTEXT1 = "#5c5f77"
            cls.SUBTEXT0 = "#6c6f85"
            cls.OVERLAY2 = "#7c7f93"
            cls.OVERLAY1 = "#8c8fa1"
            cls.OVERLAY0 = "#9ca0b0"
            cls.ROSEWATER = "#dc8a78"
            cls.FLAMINGO  = "#dd7878"
            cls.PINK      = "#ea76cb"
            cls.MAUVE     = "#8839ef"
            cls.RED       = "#d20f39"
            cls.MAROON    = "#e64553"
            cls.PEACH     = "#fe640b"
            cls.YELLOW    = "#df8e1d"
            cls.GREEN     = "#40a02b"
            cls.TEAL      = "#179299"
            cls.SKY       = "#04a5e5"
            cls.SAPPHIRE  = "#209fb5"
            cls.BLUE      = "#1e66f0"
            cls.LAVENDER  = "#7287fd"
            
            cls.ACCENT       = cls.MAUVE
            cls.ACCENT_HOVER = "#7730d6"
            cls.ACCENT_DIM   = "#6627bd"
            cls.SUCCESS = cls.GREEN
            cls.WARNING = cls.PEACH
            cls.ERROR   = cls.RED
            cls.TOAST_TEXT = cls.BASE
            cls.WINDOW_BG  = cls.BASE
            cls.SIDEBAR_BG = cls.MANTLE
            cls.BUTTON_TEXT = "#ffffff"
        else:
            # Catppuccin Mocha (reset to defaults)
            cls.CRUST    = "#11111b"
            cls.MANTLE   = "#181825"
            cls.BASE     = "#1e1e2e"
            cls.SURFACE0 = "#313244"
            cls.SURFACE1 = "#45475a"
            cls.SURFACE2 = "#585b70"
            cls.TEXT      = "#cdd6f4"
            cls.SUBTEXT1 = "#bac2de"
            cls.SUBTEXT0 = "#a6adc8"
            cls.OVERLAY2 = "#7f849c"
            cls.OVERLAY1 = "#6c7086"
            cls.OVERLAY0 = "#585b70"
            cls.ROSEWATER = "#f5e0dc"
            cls.FLAMINGO  = "#f2cdcd"
            cls.PINK      = "#f5c2e7"
            cls.MAUVE     = "#cba6f7"
            cls.RED       = "#f38ba8"
            cls.MAROON    = "#eba0ac"
            cls.PEACH     = "#fab387"
            cls.YELLOW    = "#f9e2af"
            cls.GREEN     = "#a6e3a1"
            cls.TEAL      = "#94e2d5"
            cls.SKY       = "#89dceb"
            cls.SAPPHIRE  = "#74c7ec"
            cls.BLUE      = "#89b4fa"
            cls.LAVENDER  = "#b4befe"
            
            cls.ACCENT       = cls.MAUVE
            cls.ACCENT_HOVER = "#b597e8"
            cls.ACCENT_DIM   = "#a688d9"
            cls.SUCCESS = cls.GREEN
            cls.WARNING = cls.PEACH
            cls.ERROR   = cls.RED
            cls.TOAST_TEXT = cls.CRUST
            cls.WINDOW_BG  = cls.BASE
            cls.SIDEBAR_BG = cls.MANTLE
            cls.BUTTON_TEXT = cls.TEXT

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
                color: {Theme.TEXT};
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
                border: 1px solid {Theme.MAUVE};
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
                border: 1px solid {Theme.MAUVE};
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
                padding: 8px 8px;
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
                border: 1px solid {Theme.SURFACE1};
                border-radius: 4px;
                text-align: center;
                color: {Theme.SUBTEXT1};
                height: 6px;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.BLUE};
                border-radius: 4px;
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

    @staticmethod
    def get_light_stylesheet():
        return f"""
            /* ═══ Global ═══════════════════════════════ */

            QMainWindow {{
                background-color: {Theme.LATTE_BASE};
                color: {Theme.LATTE_TEXT};
            }}
            QWidget {{
                font-family: '{Theme.FONT_FAMILY}', 'Cascadia Code', 'Consolas', monospace;
                color: {Theme.LATTE_TEXT};
                font-size: 13px;
            }}
            QLabel {{
                background: transparent;
                color: {Theme.LATTE_TEXT};
            }}
            QLabel#secondary {{
                color: {Theme.LATTE_SUBTEXT1};
            }}

            /* ═══ Sidebar & Player Bar ═══════════════ */

            QWidget#Sidebar {{
                background-color: {Theme.LATTE_MANTLE};
            }}
            QWidget#playerBar {{
                background-color: {Theme.LATTE_MANTLE};
                border-top: 1px solid {Theme.LATTE_SURFACE1};
            }}

            /* ═══ Inputs ══════════════════════════════ */

            QLineEdit {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE2};
                border-radius: 4px;
                padding: 6px 10px;
                selection-background-color: rgba(30, 102, 240, 0.25);
                selection-color: {Theme.LATTE_TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.LATTE_MAUVE};
            }}
            QLineEdit:disabled {{
                color: {Theme.LATTE_OVERLAY1};
                background-color: {Theme.LATTE_MANTLE};
                border: 1px solid {Theme.LATTE_SURFACE1};
            }}
            QTextEdit, QPlainTextEdit {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE2};
                border-radius: 4px;
                padding: 6px 10px;
                selection-background-color: rgba(30, 102, 240, 0.25);
                selection-color: {Theme.LATTE_TEXT};
            }}
            QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {Theme.LATTE_MAUVE};
            }}

            /* ═══ Buttons ═════════════════════════════ */

            QPushButton {{
                background-color: {Theme.LATTE_SURFACE1};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE2};
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: 400;
                font-size: 13px;
                min-height: 22px;
            }}
            QPushButton:hover {{
                background-color: {Theme.LATTE_SURFACE2};
                border: 1px solid {Theme.LATTE_OVERLAY1};
            }}
            QPushButton:pressed {{
                background-color: {Theme.LATTE_SURFACE0};
                border: 1px solid {Theme.LATTE_MAUVE};
            }}
            QPushButton:focus {{
                border: 1px solid {Theme.LATTE_MAUVE};
            }}
            QPushButton:disabled {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_OVERLAY1};
                border: 1px solid {Theme.LATTE_SURFACE0};
            }}

            /* Primary */
            QPushButton[class="primary"] {{
                background-color: {Theme.LATTE_MAUVE};
                color: {Theme.LATTE_BASE};
                border: none;
                font-weight: 600;
            }}
            QPushButton[class="primary"]:hover {{
                background-color: {Theme.LATTE_LAVENDER};
            }}
            QPushButton[class="primary"]:pressed {{
                background-color: {Theme.ACCENT_HOVER};
            }}
            QPushButton[class="primary"]:disabled {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_OVERLAY1};
            }}

            /* Destructive */
            QPushButton[class="destructive"] {{
                background-color: {Theme.LATTE_RED};
                color: {Theme.LATTE_BASE};
                border: none;
            }}
            QPushButton[class="destructive"]:hover {{
                background-color: {Theme.LATTE_MAROON};
            }}

            /* ═══ Combo Box ═══════════════════════════ */

            QComboBox {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE2};
                border-radius: 4px;
                padding: 6px 10px;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border: 1px solid {Theme.LATTE_MAUVE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
                selection-background-color: {Theme.LATTE_BLUE};
                selection-color: {Theme.LATTE_BASE};
                border: 1px solid {Theme.LATTE_SURFACE1};
            }}

            /* ═══ Tree Widget (File List) ════════════ */

            QTreeWidget {{
                background-color: {Theme.LATTE_BASE};
                alternate-background-color: {Theme.LATTE_MANTLE};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 8px 8px;
                border-radius: 0px;
                color: {Theme.LATTE_TEXT};
            }}
            QTreeWidget::item:alternate {{
                background-color: {Theme.LATTE_MANTLE};
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.LATTE_MAUVE};
                color: {Theme.LATTE_BASE};
            }}
            QTreeWidget::item:hover {{
                background-color: {Theme.LATTE_SURFACE0};
            }}
            QHeaderView::section {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_SUBTEXT1};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {Theme.LATTE_SURFACE1};
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
                background: {Theme.LATTE_SURFACE0};
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.LATTE_SURFACE2};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.LATTE_OVERLAY1};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {Theme.LATTE_OVERLAY2};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {Theme.LATTE_SURFACE0};
                height: 10px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.LATTE_SURFACE2};
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.LATTE_OVERLAY1};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background: {Theme.LATTE_OVERLAY2};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            /* ═══ Frames & Splitter ══════════════════ */

            QFrame {{
                background: transparent;
                border: 1px solid {Theme.LATTE_SURFACE1};
            }}
            QSplitter::handle {{
                background-color: {Theme.LATTE_SURFACE1};
            }}

            /* ═══ Dialogs & Views ════════════════════ */

            QDialog {{
                background-color: {Theme.LATTE_BASE};
                color: {Theme.LATTE_TEXT};
            }}
            QMessageBox {{
                background-color: {Theme.LATTE_BASE};
                color: {Theme.LATTE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {Theme.LATTE_TEXT};
            }}
            QFileDialog {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
            }}
            QInputDialog {{
                background-color: {Theme.LATTE_BASE};
            }}

            QListView, QTreeView {{
                background-color: {Theme.LATTE_BASE};
                alternate-background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 6px;
                outline: none;
            }}
            QListView::item:selected, QTreeView::item:selected {{
                background-color: {Theme.LATTE_MAUVE};
                color: {Theme.LATTE_BASE};
            }}
            QListView::item:hover, QTreeView::item:hover {{
                background-color: {Theme.LATTE_SURFACE0};
            }}

            /* ═══ Menus ══════════════════════════════ */

            QMenuBar {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
                border-bottom: 1px solid {Theme.LATTE_SURFACE1};
                font-size: 13px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                color: {Theme.LATTE_TEXT};
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
            }}
            QMenuBar::item:pressed {{
                background-color: {Theme.LATTE_SURFACE1};
            }}
            QMenu {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
            }}
            QMenu::separator {{
                height: 1px;
                background: {Theme.LATTE_SURFACE1};
                margin: 4px 8px;
            }}

            /* ═══ Progress ═══════════════════════════ */

            QProgressBar {{
                background-color: {Theme.LATTE_SURFACE0};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 4px;
                text-align: center;
                color: {Theme.LATTE_SUBTEXT1};
                height: 6px;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.LATTE_BLUE};
                border-radius: 4px;
            }}
            QProgressDialog {{
                background-color: {Theme.LATTE_BASE};
                color: {Theme.LATTE_TEXT};
            }}

            /* ═══ Spin Box ═══════════════════════════ */

            QSpinBox, QDoubleSpinBox {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 4px;
                padding: 6px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Theme.LATTE_MAUVE};
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {Theme.LATTE_SURFACE1};
                border: none;
                width: 16px;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {Theme.LATTE_SURFACE2};
            }}

            /* ═══ Slider ═════════════════════════════ */

            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: {Theme.LATTE_SURFACE1};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {Theme.LATTE_MAUVE};
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Theme.LATTE_LAVENDER};
            }}
            QSlider::sub-page:horizontal {{
                background: {Theme.LATTE_MAUVE};
                border-radius: 2px;
            }}

            /* ═══ Tabs ═══════════════════════════════ */

            QTabWidget::pane {{
                border: 1px solid {Theme.LATTE_SURFACE1};
                background-color: {Theme.LATTE_BASE};
                border-radius: 0px;
            }}
            QTabBar::tab {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_SUBTEXT1};
                padding: 8px 16px;
                margin-right: 0px;
                border: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
            QTabBar::tab:selected {{
                background-color: {Theme.LATTE_BASE};
                color: {Theme.LATTE_TEXT};
                border-top: 1px solid {Theme.LATTE_MAUVE};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {Theme.LATTE_SURFACE0};
            }}

            /* ═══ Checkbox & Radio ═══════════════════ */

            QCheckBox, QRadioButton {{
                background: transparent;
                color: {Theme.LATTE_TEXT};
                spacing: 8px;
                font-size: 13px;
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {Theme.LATTE_SURFACE0};
                border: 1px solid {Theme.LATTE_SURFACE1};
            }}
            QCheckBox::indicator {{
                border-radius: 3px;
            }}
            QRadioButton::indicator {{
                border-radius: 8px;
            }}
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                background-color: {Theme.LATTE_BLUE};
                border-color: {Theme.LATTE_BLUE};
            }}
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
                border-color: {Theme.LATTE_MAUVE};
            }}
            QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
                background-color: {Theme.LATTE_SURFACE0};
                border-color: {Theme.LATTE_OVERLAY1};
            }}

            /* ═══ Group Box ══════════════════════════ */

            QGroupBox {{
                background: transparent;
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {Theme.LATTE_SUBTEXT0};
                font-size: 11px;
            }}

            /* ═══ Tooltip ════════════════════════════ */

            QToolTip {{
                background-color: {Theme.LATTE_SURFACE0};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE2};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}

            /* ═══ Status Bar ═════════════════════════ */

            QStatusBar {{
                background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_SUBTEXT1};
                font-size: 11px;
            }}

            /* ═══ List Widget ════════════════════════ */

            QListWidget {{
                background-color: {Theme.LATTE_BASE};
                alternate-background-color: {Theme.LATTE_MANTLE};
                color: {Theme.LATTE_TEXT};
                border: 1px solid {Theme.LATTE_SURFACE1};
                border-radius: 6px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 0px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.LATTE_MAUVE};
                color: {Theme.LATTE_BASE};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.LATTE_SURFACE0};
            }}

            /* ═══ Dialog Button Box ══════════════════ */

            QDialogButtonBox {{
                button-layout: 3;
            }}
        """

    @classmethod
    def current_stylesheet(cls):
        return cls.get_light_stylesheet() if cls._is_light else cls.get_stylesheet()
