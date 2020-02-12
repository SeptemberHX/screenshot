from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QButtonGroup, QFrame, QHBoxLayout

from pyqt_screenshot.constant import *
from PyQt5.QtCore import pyqtSignal, Qt

import resource.resource


class MyToolBar(QWidget):
    """ ToolBar widget """

    # signal
    trigger = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MyToolBar, self).__init__(parent)

        self.setWindowFlags(Qt.ToolTip)
        self.paddingX = 5
        self.paddingY = 2
        self.iconWidth = self.iconHeight = 28
        self.setFixedHeight(self.iconHeight + 2 * self.paddingY)
        self.setFixedWidth(300)

        self.initWindow()

    def initDrawButtons(self):
        # draw action buttons
        self.rectButton = QPushButton(self)
        self.rectButton.setIcon(QIcon(":/resource/icon/rect.png"))
        self.rectButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.rectButton.setCheckable(True)

        self.ellipseButton = QPushButton(self)
        self.ellipseButton.setIcon(QIcon(":/resource/icon/ellipse.png"))
        self.ellipseButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.ellipseButton.setCheckable(True)

        self.arrowButton = QPushButton(self)
        self.arrowButton.setIcon(QIcon(":/resource/icon/arrow.png"))
        self.arrowButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.arrowButton.setCheckable(True)

        self.lineButton = QPushButton(self)
        self.lineButton.setIcon(QIcon(":/resource/icon/line.png"))
        self.lineButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.lineButton.setCheckable(True)

        self.freePenButton = QPushButton(self)
        self.freePenButton.setIcon(QIcon(":/resource/icon/pen.png"))
        self.freePenButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.freePenButton.setCheckable(True)

        self.textButton = QPushButton(self)
        self.textButton.setIcon(QIcon(":/resource/icon/text.png"))
        self.textButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.textButton.setCheckable(True)

        self.drawButtonGroup = QButtonGroup(self)
        self.drawButtonGroup.addButton(self.rectButton)
        self.drawButtonGroup.addButton(self.ellipseButton)
        self.drawButtonGroup.addButton(self.arrowButton)
        self.drawButtonGroup.addButton(self.lineButton)
        self.drawButtonGroup.addButton(self.freePenButton)
        self.drawButtonGroup.addButton(self.textButton)
        self.drawButtonGroup.buttonClicked.connect(self.buttonToggled)

        self.buttonList = [self.rectButton, self.ellipseButton, self.arrowButton,
                           self.freePenButton, self.lineButton, self.textButton]

        self.hlayout.addWidget(self.rectButton)
        self.hlayout.addWidget(self.ellipseButton)
        self.hlayout.addWidget(self.arrowButton)
        self.hlayout.addWidget(self.lineButton)
        self.hlayout.addWidget(self.freePenButton)
        self.hlayout.addWidget(self.textButton)

    def initOtherButtons(self):
        # other action buttons
        self.separator1 = QFrame(self)
        self.separator1.setFrameShape(QFrame.VLine)
        self.separator1.setFrameShadow(QFrame.Sunken)

        self.undoButton = QPushButton(self)
        self.undoButton.setIcon(QIcon(":/resource/icon/undo.png"))
        self.undoButton.setFixedSize(self.iconWidth, self.iconWidth)
        self.undoButton.clicked.connect(self.otherButtonsClicked)

        self.saveButton = QPushButton(self)
        self.saveButton.setIcon(QIcon(":/resource/icon/save.png"))
        self.saveButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.saveButton.clicked.connect(self.otherButtonsClicked)

        self.separator2 = QFrame(self)
        self.separator2.setFrameShape(QFrame.VLine)
        self.separator2.setFrameShadow(QFrame.Sunken)

        self.cancelButton = QPushButton(self)
        self.cancelButton.setIcon(QIcon(":/resource/icon/close.png"))
        self.cancelButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.cancelButton.clicked.connect(self.otherButtonsClicked)

        self.okButton = QPushButton(self)
        self.okButton.setIcon(QIcon(":/resource/icon/check.png"))
        self.okButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.okButton.clicked.connect(self.otherButtonsClicked)

        self.hlayout.addWidget(self.separator1)
        self.hlayout.addWidget(self.undoButton)
        self.hlayout.addWidget(self.saveButton)
        self.hlayout.addWidget(self.separator2)
        self.hlayout.addWidget(self.cancelButton)
        self.hlayout.addWidget(self.okButton)

    def initWindow(self):
        self.hlayout = QHBoxLayout()
        self.hlayout.setSpacing(2)
        self.hlayout.setContentsMargins(10, 2, 10, 2)
        self.setLayout(self.hlayout)

        self.initDrawButtons()
        self.initOtherButtons()

    # slots
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
        elif button == self.arrowButton:
            self.trigger.emit(ACTION_ARROW)
        elif button == self.lineButton:
            self.trigger.emit(ACTION_LINE)
        elif button == self.freePenButton:
            self.trigger.emit(ACTION_FREEPEN)
        elif button == self.textButton:
            self.trigger.emit(ACTION_TEXT)
        else:
            pass

    def otherButtonsClicked(self):
        if self.sender() == self.undoButton:
            self.trigger.emit(ACTION_UNDO)
        elif self.sender() == self.cancelButton:
            self.trigger.emit(ACTION_CANCEL)
        elif self.sender() == self.okButton:
            self.trigger.emit(ACTION_SURE)
        elif self.sender() == self.saveButton:
            self.trigger.emit(ACTION_SAVE)
