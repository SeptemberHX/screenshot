from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QButtonGroup, QFrame, QHBoxLayout

from pyqt_screenshot import constant
from pyqt_screenshot.constant import *
from PyQt5.QtCore import pyqtSignal, Qt

import resource.resource


class MyToolBar(QWidget):
    """ ToolBar widget """

    # signal
    trigger = pyqtSignal(int)

    def __init__(self, flags, parent=None):
        super(MyToolBar, self).__init__(parent)

        self.setWindowFlags(Qt.ToolTip)
        self.paddingX = 5
        self.paddingY = 2
        self.iconWidth = self.iconHeight = 28
        self.setFixedHeight(self.iconHeight + 2 * self.paddingY)
        # self.setFixedWidth(300)

        self.rectButton = None
        self.ellipseButton = None
        self.arrowButton = None
        self.lineButton = None
        self.freePenButton = None
        self.textButton = None
        self.undoButton = None
        self.cancelButton = None
        self.okButton = None
        self.saveButton = None
        self.button_list = []

        self.initWindow(flags)

    def initDrawButtons(self, flags):
        self.drawButtonGroup = QButtonGroup(self)

        # draw action buttons
        if flags & constant.RECT:
            self.rectButton = QPushButton(self)
            self.rectButton.setIcon(QIcon(":/resource/icon/rect.png"))
            self.rectButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.rectButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.rectButton)
            self.hlayout.addWidget(self.rectButton)
            self.button_list.append(self.rectButton)

        if flags & constant.ELLIPSE:
            self.ellipseButton = QPushButton(self)
            self.ellipseButton.setIcon(QIcon(":/resource/icon/ellipse.png"))
            self.ellipseButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.ellipseButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.ellipseButton)
            self.hlayout.addWidget(self.ellipseButton)
            self.button_list.append(self.ellipseButton)

        if flags & constant.ARROW:
            self.arrowButton = QPushButton(self)
            self.arrowButton.setIcon(QIcon(":/resource/icon/arrow.png"))
            self.arrowButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.arrowButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.arrowButton)
            self.hlayout.addWidget(self.arrowButton)
            self.button_list.append(self.arrowButton)

        if flags & constant.LINE:
            self.lineButton = QPushButton(self)
            self.lineButton.setIcon(QIcon(":/resource/icon/line.png"))
            self.lineButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.lineButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.lineButton)
            self.hlayout.addWidget(self.lineButton)
            self.button_list.append(self.lineButton)

        if flags & constant.FREEPEN:
            self.freePenButton = QPushButton(self)
            self.freePenButton.setIcon(QIcon(":/resource/icon/pen.png"))
            self.freePenButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.freePenButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.freePenButton)
            self.hlayout.addWidget(self.freePenButton)
            self.button_list.append(self.freePenButton)

        if flags & constant.TEXT:
            self.textButton = QPushButton(self)
            self.textButton.setIcon(QIcon(":/resource/icon/text.png"))
            self.textButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.textButton.setCheckable(True)
            self.drawButtonGroup.addButton(self.textButton)
            self.hlayout.addWidget(self.textButton)
            self.button_list.append(self.textButton)

        self.drawButtonGroup.buttonClicked.connect(self.buttonToggled)

    def initOtherButtons(self, flags):
        # other action buttons
        if len(self.button_list) != 0:
            self.separator1 = QFrame(self)
            self.separator1.setFrameShape(QFrame.VLine)
            self.separator1.setFrameShadow(QFrame.Sunken)
            self.hlayout.addWidget(self.separator1)

            self.undoButton = QPushButton(self)
            self.undoButton.setIcon(QIcon(":/resource/icon/undo.png"))
            self.undoButton.setFixedSize(self.iconWidth, self.iconWidth)
            self.undoButton.clicked.connect(self.otherButtonsClicked)
            self.hlayout.addWidget(self.undoButton)

        if flags & constant.SAVE_TO_FILE:
            self.saveButton = QPushButton(self)
            self.saveButton.setIcon(QIcon(":/resource/icon/save.png"))
            self.saveButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.saveButton.clicked.connect(self.otherButtonsClicked)
            self.hlayout.addWidget(self.saveButton)

        self.separator2 = QFrame(self)
        self.separator2.setFrameShape(QFrame.VLine)
        self.separator2.setFrameShadow(QFrame.Sunken)
        self.hlayout.addWidget(self.separator2)

        self.cancelButton = QPushButton(self)
        self.cancelButton.setIcon(QIcon(":/resource/icon/close.png"))
        self.cancelButton.setFixedSize(self.iconWidth, self.iconHeight)
        self.cancelButton.clicked.connect(self.otherButtonsClicked)

        if flags & constant.CLIPBOARD:
            self.okButton = QPushButton(self)
            self.okButton.setIcon(QIcon(":/resource/icon/check.png"))
            self.okButton.setFixedSize(self.iconWidth, self.iconHeight)
            self.okButton.clicked.connect(self.otherButtonsClicked)
            self.hlayout.addWidget(self.okButton)

        self.hlayout.addWidget(self.cancelButton)

    def initWindow(self, flags):
        self.hlayout = QHBoxLayout()
        self.hlayout.setSpacing(2)
        self.hlayout.setContentsMargins(10, 2, 10, 2)
        self.setLayout(self.hlayout)

        self.initDrawButtons(flags)
        self.initOtherButtons(flags)

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
