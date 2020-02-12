import sys

from PyQt5.QtWidgets import QApplication
from pyqt_screenshot.screenshot import MainWindow

if __name__ == "__main__":
    qtApp = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    qtApp.exec()
