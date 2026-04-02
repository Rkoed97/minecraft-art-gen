"""Project folder selection screen."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QGroupBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from minecraft_art_gen.utils.validators import validate_project_path

_SETTINGS_KEY = "recent_projects"
_MAX_RECENT = 8


class ProjectScreen(QWidget):
    project_selected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._load_recent()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 40, 60, 40)
        root.setSpacing(20)

        title = QLabel("Minecraft Art Gen")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Select a project folder to get started")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        root.addSpacing(10)

        # Folder picker row
        picker_group = QGroupBox("Project Folder")
        picker_layout = QHBoxLayout(picker_group)
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Choose a folder…")
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        picker_layout.addWidget(self._path_edit)
        picker_layout.addWidget(browse_btn)
        root.addWidget(picker_group)

        # Recent folders
        recent_group = QGroupBox("Recent Folders")
        recent_layout = QVBoxLayout(recent_group)
        self._recent_list = QListWidget()
        self._recent_list.setMaximumHeight(160)
        self._recent_list.itemDoubleClicked.connect(self._select_recent)
        recent_layout.addWidget(self._recent_list)
        root.addWidget(recent_group)

        root.addStretch()

        # Continue button
        self._continue_btn = QPushButton("Continue →")
        self._continue_btn.setFixedHeight(40)
        self._continue_btn.setDefault(True)
        self._continue_btn.clicked.connect(self._confirm)
        root.addWidget(self._continue_btn)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder", self._path_edit.text() or "")
        if path:
            self._path_edit.setText(path)

    def _confirm(self) -> None:
        path = self._path_edit.text().strip()
        try:
            validate_project_path(path)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Path", str(exc))
            return
        self._save_recent(path)
        self.project_selected.emit(path)

    def _select_recent(self, item: QListWidgetItem) -> None:
        self._path_edit.setText(item.text())
        self._confirm()

    def _load_recent(self) -> None:
        from PySide6.QtCore import QSettings
        settings = QSettings("MinecraftArtGen", "App")
        recent = settings.value(_SETTINGS_KEY, [])
        if isinstance(recent, str):
            recent = [recent]
        self._recent_list.clear()
        for p in recent:
            self._recent_list.addItem(p)

    def _save_recent(self, path: str) -> None:
        from PySide6.QtCore import QSettings
        import os
        settings = QSettings("MinecraftArtGen", "App")
        recent = settings.value(_SETTINGS_KEY, [])
        if isinstance(recent, str):
            recent = [recent]
        recent = [p for p in recent if p != path]
        recent.insert(0, path)
        recent = recent[:_MAX_RECENT]
        settings.setValue(_SETTINGS_KEY, recent)
        self._load_recent()
