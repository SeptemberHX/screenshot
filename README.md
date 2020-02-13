# A Screenshot module that supports modification during taking the screenshot #

A screenshot module writen in python with pyQt5.

It supports:

| Flag | Description |
| ---- | ----        |
| `pyqt_screenshot.constant.RECT` | tool for drawing rectangle |
| `pyqt_screenshot.constant.ELLIPSE` | tool for drawing ellipse |
| `pyqt_screenshot.constant.LINE` | tool for drawing line |
| `pyqt_screenshot.constant.FREEPEN` | tool for drawing freely |
| `pyqt_screenshot.constant.TEXT` | tool for adding text |
| `pyqt_screenshot.constant.ARROW` | tool for drawing arrow |
| `pyqt_screenshot.constant.CLIPBOARD` | tool for saving to clipboard |
| `pyqt_screenshot.constant.SAVE_TO_FILE` | tool for saving to file |

You can take some simple changes after taking a screenshot without opening an image editor.

Save image as png or jpg file, or cpoy to clipboard

## Usage

```python
from pyqt_screenshot.screenshot import Screenshot, constant

img = Screenshot.take_screenshot(constant.CLIPBOARD)  # QImage or None
```

None will be returned if canceled.

```python
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel
from pyqt_screenshot.screenshot import Screenshot, constant

if __name__ == "__main__":
    qtApp = QApplication(sys.argv)

    main_window = QLabel()
    img = Screenshot.take_screenshot(constant.CLIPBOARD | constant.LINE)
    main_window.show()
    if img is not None:
        main_window.setPixmap(QPixmap(img))
    qtApp.exec()
```

## Demo

Before starting, you should make sure you have python and pyqt5 installed.

1. git clone https://github.com/SeptemberHX/screenshot.git
2. cd ./screenshot
3. python ./main.py

## Screenshot
Rectangle
![image](https://raw.githubusercontent.com/SeptemberHX/screenshot/master/screenshot/rect.png)

Ellipse
![image](https://raw.githubusercontent.com/SeptemberHX/screenshot/master/screenshot/ellipse.png)

Arrow
![image](https://raw.githubusercontent.com/SeptemberHX/screenshot/master/screenshot/arrow.png)

Line and Pen
![image](https://raw.githubusercontent.com/SeptemberHX/screenshot/master/screenshot/line_pen.png)

Text
![image](https://raw.githubusercontent.com/SeptemberHX/screenshot/master/screenshot/text.png)

## Bugs

Can't save screenshot to clipboard on Linux because the clipboard on Linux only stores the reference to the picture object, which means the clipboard can't hold the screenshot after closing the screenshot.