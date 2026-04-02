"""Main application window with screen navigation."""

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent

from src.models.asset_type import AssetType


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Minecraft Art Gen")
        self.setMinimumSize(800, 600)

        self._project_path: str = ""
        self._selected_asset_type: AssetType | None = None

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Import here to avoid circular imports at module level
        from src.screens.project_screen import ProjectScreen
        from src.screens.asset_screen import AssetScreen
        from src.screens.editor_screen import EditorScreen

        self._project_screen = ProjectScreen()
        self._asset_screen = AssetScreen()
        self._editor_screen = EditorScreen()

        self._stack.addWidget(self._project_screen)   # index 0
        self._stack.addWidget(self._asset_screen)     # index 1
        self._stack.addWidget(self._editor_screen)    # index 2

        # Connect signals
        self._project_screen.project_selected.connect(self._on_project_selected)
        self._asset_screen.asset_selected.connect(self._on_asset_selected)
        self._asset_screen.open_file_requested.connect(self._on_open_file)
        self._asset_screen.back_requested.connect(self._go_to_project_screen)
        self._editor_screen.back_requested.connect(self._go_to_asset_screen)

        self._stack.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _go_to_project_screen(self) -> None:
        self._stack.setCurrentIndex(0)

    def _go_to_asset_screen(self) -> None:
        self._stack.setCurrentIndex(1)

    def _go_to_editor_screen(self) -> None:
        self._stack.setCurrentIndex(2)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_project_selected(self, path: str) -> None:
        self._project_path = path
        self._asset_screen.set_project_path(path)
        self._go_to_asset_screen()

    def _on_asset_selected(self, asset_type: AssetType, width: int, height: int) -> None:
        self._selected_asset_type = asset_type
        self._editor_screen.new_canvas(asset_type, width, height, self._project_path)
        self._go_to_editor_screen()

    def _on_open_file(self, file_path: str) -> None:
        from src.io.png_reader import load_png
        try:
            pixel_image = load_png(file_path)
        except (ValueError, OSError) as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Open Failed", str(exc))
            return
        self._editor_screen.load_canvas(pixel_image, file_path, self._project_path)
        self._go_to_editor_screen()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._stack.currentIndex() == 2 and self._editor_screen.is_dirty():
            from PySide6.QtWidgets import QMessageBox
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        event.accept()
