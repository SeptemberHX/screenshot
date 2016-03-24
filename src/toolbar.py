from PyQt5.Qt import *
from sys import argv
from constant import *
from PyQt5.QtCore import QObject, pyqtSignal

class MyToolBar(QWidget):
    """ ToolBar widget """

    trigger = pyqtSignal(int)

    def __init__(self, parent=None):

        # signal
        super(MyToolBar, self).__init__(parent)
        self.hlayout = QHBoxLayout()
        self.parent = parent

        self.setWindowFlags(Qt.ToolTip)

        self.paddingX = 5
        self.paddingY = 2
        self.iconWidth = self.iconHeight = 28
        self.setFixedHeight(self.iconHeight + 2 * self.paddingY)
        self.setFixedWidth(300)

        # draw action buttons
        self.rectButton = QPushButton('R', self)
        self.rectButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.rectButton.setCheckable(True)

        self.ellipseButton = QPushButton('E', self)
        self.ellipseButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.ellipseButton.setCheckable(True)

        self.arrowButton = QPushButton('A', self)
        self.arrowButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.arrowButton.setCheckable(True)

        self.lineButton = QPushButton('L', self)
        self.lineButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.lineButton.setCheckable(True)

        self.textButton = QPushButton('T', self)
        self.textButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.textButton.setCheckable(True)

        self.separator1 = QFrame(self)
        self.separator1.setFrameShape(QFrame.VLine)
        self.separator1.setFrameShadow(QFrame.Sunken)

        self.drawButtonGroup = QButtonGroup(self)
        self.drawButtonGroup.addButton(self.rectButton)
        self.drawButtonGroup.addButton(self.ellipseButton)
        self.drawButtonGroup.addButton(self.arrowButton)
        self.drawButtonGroup.addButton(self.lineButton)
        self.drawButtonGroup.addButton(self.textButton)
        self.drawButtonGroup.buttonClicked.connect(self.buttonToggled)

        # other action buttons
        self.undoButton = QPushButton('U', self)
        self.undoButton.setFixedSize(self.iconWidth, self.iconWidth)
        self.undoButton.toggled.connect(self.buttonToggled)

        self.saveButton = QPushButton('S', self)
        self.saveButton.setFixedSize(self.iconWidth, self.iconHeight)

        self.separator2 = QFrame(self)
        self.separator2.setFrameShape(QFrame.VLine)
        self.separator2.setFrameShadow(QFrame.Sunken)

        self.cancelButton = QPushButton('C', self)
        self.cancelButton.setFixedSize(self.iconWidth, self.iconHeight)

        self.okButton = QPushButton('O', self)
        self.okButton.setFixedSize(self.iconWidth, self.iconHeight)

        self.hlayout.addWidget(self.rectButton)
        self.hlayout.addWidget(self.ellipseButton)
        self.hlayout.addWidget(self.arrowButton)
        self.hlayout.addWidget(self.lineButton)
        self.hlayout.addWidget(self.textButton)
        self.hlayout.addWidget(self.separator1)
        self.hlayout.addWidget(self.undoButton)
        self.hlayout.addWidget(self.saveButton)
        self.hlayout.addWidget(self.separator2)
        self.hlayout.addWidget(self.cancelButton)
        self.hlayout.addWidget(self.okButton)


        self.hlayout.setSpacing(2)
        self.hlayout.setContentsMargins(10, 0, 10, 0)

        self.setLayout(self.hlayout)

        self.buttonList = [self.rectButton, self.ellipseButton, self.arrowButton,
                           self.lineButton, self.textButton, self.undoButton]



    def buttonToggled(self, button):
        """
        :type button: QPushButton
        :param button:
        :return:
        """
        if button == self.rectButton:
            self.trigger.emit(ACTION_RECT)
        elif button == self.ellipseButton:
            self.trigger.emit(ACTION_ELLIPSE)
        else:
            pass



if __name__ == '__main__':
    a = QApplication(argv)
    test = MyToolBar()
    test.move(100, 200)
    test.show()

    a.exec_()
