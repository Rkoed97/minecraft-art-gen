"""Application entry point."""

import sys
import os

# Disable HiDPI auto-scaling for pixel-perfect rendering
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "0")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from minecraft_art_gen.app import MainWindow


def main() -> None:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DisableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Minecraft Art Gen")
    app.setOrganizationName("MinecraftArtGen")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
