import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel
from pyqt_screenshot.screenshot import Screenshot, constant

if __name__ == "__main__":
    qtApp = QApplication(sys.argv)

    main_window = QLabel()
    img = Screenshot.take_screenshot(constant.CLIPBOARD)
    main_window.show()
    if img is not None:
        main_window.setPixmap(QPixmap(img))
    qtApp.exec()
