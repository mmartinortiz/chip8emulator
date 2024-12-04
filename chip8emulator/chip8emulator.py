import argparse
import sys
from pathlib import Path
from typing import List

from bitarray import bitarray
from loguru import logger
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
)

from chip8emulator.graphics import Graphics
from chip8emulator.keypad import Keypad
from chip8emulator.memory import Memory
from chip8emulator.processor import Processor

parser = argparse.ArgumentParser()
parser.add_argument("rom_path", nargs="?", default="roms/IBM Logo.ch8")
parser.add_argument("--ips", type=int, default=10, help="Instructions per second")
parser.add_argument(
    "--debug",
    action="store_true",
    help="Set loguru level to debug",
)
args = parser.parse_args()

logger.remove()
logger.add(sys.stderr, level="DEBUG" if args.debug else "INFO")


class Chip8Screen(QGraphicsView):
    def __init__(self, graphic_system: Graphics, scale_factor: int = 10):
        super().__init__()
        self.width = graphic_system.width
        self.height = graphic_system.height
        self.setMinimumSize(
            self.width * scale_factor,
            self.height * scale_factor,
        )
        self.scale(scale_factor, scale_factor)

        # Scene is the container that holds all the graphical elements
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Image is the actual image that will be rendered
        self.image = QImage(self.width, self.height, QImage.Format_Mono)
        self.scene.addPixmap(QPixmap.fromImage(self.image))

    def refresh(self, pixels: List[bitarray]):
        self.scene.clear()

        # Update the image with the current status of the pixels
        for y, row in enumerate(pixels):
            for x, pixel in enumerate(row):
                self.image.setPixel(x, y, int(pixel))

        self.scene.addPixmap(QPixmap.fromImage(self.image))


class Chip8MainWindow(QMainWindow):
    """
    The main window of the Chip-8 emulator application. It contains all the widgets
    and graphical elements of the application. It also handles the key events.
    """

    def __init__(self, chip8: Processor, screen: Chip8Screen):
        super().__init__()
        self.chip8 = chip8
        self.setCentralWidget(screen)
        self.setWindowTitle("Chip-8 Emulator")

        self.keymap = {
            Qt.Key.Key_1: 0x1,
            Qt.Key.Key_2: 0x2,
            Qt.Key.Key_3: 0x3,
            Qt.Key.Key_4: 0xC,
            Qt.Key.Key_Q: 0x4,
            Qt.Key.Key_W: 0x5,
            Qt.Key.Key_E: 0x6,
            Qt.Key.Key_R: 0xD,
            Qt.Key.Key_A: 0x7,
            Qt.Key.Key_S: 0x8,
            Qt.Key.Key_D: 0x9,
            Qt.Key.Key_F: 0xE,
            Qt.Key.Key_Z: 0xA,
            Qt.Key.Key_X: 0x0,
            Qt.Key.Key_C: 0xB,
            Qt.Key.Key_V: 0xF,
        }

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.keymap:
            self.chip8.keypad.press_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close()
        elif key == Qt.Key.Key_P:
            print(self.chip8.graphics)

        if key in self.keymap:
            self.chip8.keypad.release_key(self.keymap[key])
        else:
            logger.debug(f"Key {key} not mapped")


class Chip8Application(QApplication):
    """
    The application itself. If creates the Application window where the Emulator will
    be rendered and the Chip-8 emulator itself.

    This is the class that controls when the emulator runs its cycles and updates the
    screen of the emulated system.
    """

    def __init__(self, rom: Path, ips: int = 10):
        """
        Args:
            rom (Path): Path to the ROM file that will be loaded into the emulator.
            ips (int, optional): Instructions Per Second. Defaults to 7.
        """
        super().__init__()
        self.processor = Processor(
            memory=Memory(),
            graphics=Graphics(),
            keypad=Keypad(),
        )
        self.processor.reset()
        self.rom = rom
        self.ips = ips

        # Differences between the Window and the Screen:
        # - The Window contains all the elements visible to the user
        # - The Screen is the area where the CHIP-8 graphics are rendered
        # The screen is used directly to update the rendered image with the content
        # of the CHIP-8 graphics. It is also passed to the Window, so it can be
        # incorporated to the main window application.
        self.screen = Chip8Screen(self.processor.graphics)
        self.main_window = Chip8MainWindow(self.processor, self.screen)

        self.timer = QTimer()
        self.timer.setInterval(1 / self.ips * 1000)
        self.timer.timeout.connect(self.update)

    def start(self):
        """
        After initialization, start the application.
        """
        # Load the ROM into memory
        self.processor.reset()
        self.processor.load_program(self.rom)
        logger.debug(f"ROM {self.rom} loaded into memory")

        # Start the timer that will trigger the emulator's cycles
        self.timer.start()

        # Show the main window
        self.main_window.show()

    def update(self):
        self.processor.emulate(7)
        if self.processor.redraw:
            self.screen.refresh(self.processor.graphics.pixels)


def main():
    app = Chip8Application(rom=Path(args.rom_path), ips=args.ips)
    app.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
