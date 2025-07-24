from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QDialogButtonBox, QFontDialog, QLabel
)
from PyQt6.QtCore import pyqtSignal

class SettingsDialog(QDialog):
    """A dialog for changing application settings like language and font."""
    settings_changed = pyqtSignal()

    def __init__(self, db_manager, translator, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.translator = translator
        
        self.setWindowTitle(self.translator.get_text("settings_title"))
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "فارسی (Persian)"])
        current_lang = self.db_manager.get_setting("language", "en")
        self.language_combo.setCurrentIndex(0 if current_lang == "en" else 1)
        form_layout.addRow(self.translator.get_text("language"), self.language_combo)

        # Font selection
        self.font_button = QPushButton(self.translator.get_text("select_font"))
        self.font_button.clicked.connect(self.select_font)
        self.font_label = QLabel(self.db_manager.get_setting("font_family", "Default"))
        form_layout.addRow(self.translator.get_text("font"), self.font_button)
        form_layout.addRow(self.translator.get_text("current_font"), self.font_label)
        
        layout.addLayout(form_layout)

        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_font(self):
        """Opens a font dialog to choose a new font."""
        current_font_family = self.font_label.text()
        current_font = QFont(current_font_family) if current_font_family != "Default" else QFont()
        
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.font_label.setText(font.family())

    def accept(self):
        """Saves the settings and closes the dialog."""
        # Save language
        lang_code = "en" if self.language_combo.currentIndex() == 0 else "fa"
        self.db_manager.set_setting("language", lang_code)
        
        # Save font
        font_family = self.font_label.text()
        self.db_manager.set_setting("font_family", font_family)

        self.settings_changed.emit()
        super().accept()
