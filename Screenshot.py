import sys

from PyQt5.QtWidgets import QApplication
from pyqt_screenshot.screenshot import Screenshot, constant

if __name__ == "__main__":
    qtApp = QApplication(sys.argv)
    window = Screenshot(constant.CLIPBOARD | constant.TEXT | constant.RECT | constant.ARROW | constant.FREEPEN
                        | constant.LINE | constant.ELLIPSE | constant.SAVE_TO_FILE)
    window.show()
    qtApp.exec()
