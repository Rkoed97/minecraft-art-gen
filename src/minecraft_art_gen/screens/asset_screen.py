"""Asset type selection screen."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QGroupBox, QComboBox, QMessageBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from minecraft_art_gen.models.asset_type import ASSET_TYPES, ASSET_TYPE_ORDER, AssetType

# Asset types that support resolution variants
_MULTI_VARIANT_KEYS = {"block", "item", "trim"}


class AssetScreen(QWidget):
    asset_selected = Signal(AssetType, int, int)  # asset_type, width, height
    open_file_requested = Signal(str)             # file_path
    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._project_path: str = ""
        self._build_ui()
        self._populate_list()

    def set_project_path(self, path: str) -> None:
        self._project_path = path
        self._project_label.setText(f"Project: {path}")

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(60, 30, 60, 30)
        root.setSpacing(16)

        title = QLabel("Choose Asset Type")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        root.addWidget(title)

        self._project_label = QLabel()
        self._project_label.setStyleSheet("color: gray; font-size: 11px;")
        root.addWidget(self._project_label)

        # Asset list
        list_group = QGroupBox("Asset Types")
        list_layout = QVBoxLayout(list_group)
        self._asset_list = QListWidget()
        self._asset_list.currentItemChanged.connect(self._on_asset_changed)
        self._asset_list.itemDoubleClicked.connect(self._confirm_create)
        list_layout.addWidget(self._asset_list)
        root.addWidget(list_group)

        # Resolution variant selector (shown only for multi-variant types)
        self._variant_group = QGroupBox("Resolution")
        variant_layout = QHBoxLayout(self._variant_group)
        self._variant_combo = QComboBox()
        variant_layout.addWidget(QLabel("Size:"))
        variant_layout.addWidget(self._variant_combo)
        variant_layout.addStretch()
        root.addWidget(self._variant_group)
        self._variant_group.setVisible(False)

        # Buttons row
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.back_requested)
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()

        open_btn = QPushButton("Open Existing PNG…")
        open_btn.clicked.connect(self._open_file)
        btn_layout.addWidget(open_btn)

        create_btn = QPushButton("Create →")
        create_btn.setDefault(True)
        create_btn.setFixedHeight(36)
        create_btn.clicked.connect(self._confirm_create)
        btn_layout.addWidget(create_btn)

        root.addLayout(btn_layout)

    def _populate_list(self) -> None:
        self._asset_list.clear()
        for key in ASSET_TYPE_ORDER:
            at = ASSET_TYPES[key]
            item = QListWidgetItem(f"{at.name}  —  {at.default_width}×{at.default_height}")
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._asset_list.addItem(item)
        self._asset_list.setCurrentRow(0)

    def _on_asset_changed(self, current: QListWidgetItem | None, _previous) -> None:
        if current is None:
            self._variant_group.setVisible(False)
            return
        key: str = current.data(Qt.ItemDataRole.UserRole)
        at = ASSET_TYPES[key]
        if key in _MULTI_VARIANT_KEYS and len(at.variants) > 1:
            self._variant_combo.clear()
            for w, h in at.variants:
                self._variant_combo.addItem(f"{w}×{h}", (w, h))
            self._variant_group.setVisible(True)
        else:
            self._variant_group.setVisible(False)

    def _current_asset_and_size(self) -> tuple[AssetType, int, int] | None:
        item = self._asset_list.currentItem()
        if item is None:
            return None
        key: str = item.data(Qt.ItemDataRole.UserRole)
        at = ASSET_TYPES[key]
        if key in _MULTI_VARIANT_KEYS and len(at.variants) > 1:
            w, h = self._variant_combo.currentData()
        else:
            w, h = at.default_size
        return at, w, h

    def _confirm_create(self, *_) -> None:
        result = self._current_asset_and_size()
        if result is None:
            QMessageBox.warning(self, "No Selection", "Please select an asset type.")
            return
        at, w, h = result
        self.asset_selected.emit(at, w, h)

    def _open_file(self) -> None:
        start_dir = self._project_path or ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open PNG", start_dir, "PNG Images (*.png)"
        )
        if path:
            self.open_file_requested.emit(path)
