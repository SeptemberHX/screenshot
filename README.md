# A simple screenshot tool #

A simple screenshot tool writes in python with pyQt5.

You can take some simple changes after taking a screenshot without opening an image editor.

Save image as png or jpg file, or cpoy to clipboard

## How to use

Before starting, you should make sure you have python and pyqt5 installed.

1. git clone https://github.com/SeptemberHX/screenshot.git
2. cd ./src
3. python ./screenshot.py

##### Functions

You can edit pictures after taking a screenshot.

For now, you can draw RECTANGLE, ELLIPSE, ARROW and LINE. Also you can use a pen and put some TEXT on screenshot

toolbar:
rectangle ellipse arrow line pen text | undo save | close save_to_clipboard

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

Can't save screenshot to clipboard for now