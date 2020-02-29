from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame, QButtonGroup, QGridLayout, QFontDialog, \
    QSizePolicy

from pyqt_screenshot.constant import *
from PyQt5.QtCore import pyqtSignal, Qt

from resource import resource


class PenSetWidget(QWidget):

    penSizeTrigger = pyqtSignal(int)
    penColorTrigger = pyqtSignal(str)
    fontChangeTrigger = pyqtSignal(QFont)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.paddingX = 5
        self.paddingY = 2
        self.iconWidth = self.iconHeight = 24
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setWindowFlags(Qt.ToolTip)

        self.initWindows()

        self.prevSizeButton = self.penSize1
        self.penSize1.setChecked(True)
        self.presentColor.setStyleSheet('QPushButton { background-color: %s; }' % PENCOLOR)

    def generateButtons(self, parent=None):
        """ Generate buttons due to colorDic """
        self.colorButtons = []
        for color in self.colorList:
            button = QPushButton(parent)
            button.setObjectName(color[0])
            button.setStyleSheet('QPushButton { background-color: %s; }' % color[1])
            button.setFixedSize(self.iconWidth / 2, self.iconHeight / 2)
            button.setCheckable(True)
            self.colorButtons.append(button)

    def initWindows(self):
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(5, 2, 5, 2)

        self.initPenSizeButtons()
        self.initFontWidget()
        self.initPenColorButtons()

        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addWidget(self.penSize)
        self.mainLayout.addWidget(self.changeFontButton)
        self.mainLayout.addWidget(self.separator)

        self.mainLayout.addWidget(self.colorSet)

    def initPenSizeButtons(self):
        self.penSize = QWidget(self)
        self.penSizeLayout = QHBoxLayout()
        self.penSize.setLayout(self.penSizeLayout)
        # adjust pen size
        self.penSize1 = QPushButton(self.penSize)
        self.penSize1.setIcon(QIcon(":/resource/icon/pensize1.png"))
        self.penSize1.setObjectName('1')
        self.penSize1.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize1.setCheckable(True)

        self.penSize2 = QPushButton(self.penSize)
        self.penSize2.setIcon(QIcon(":/resource/icon/pensize2.png"))
        self.penSize2.setObjectName('2')
        self.penSize2.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize2.setCheckable(True)

        self.penSize3 = QPushButton(self.penSize)
        self.penSize3.setIcon(QIcon(":/resource/icon/pensize3.png"))
        self.penSize3.setObjectName('3')
        self.penSize3.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize3.setCheckable(True)

        self.sizeButtonGroup = QButtonGroup(self.penSize)
        self.sizeButtonGroup.addButton(self.penSize1)
        self.sizeButtonGroup.addButton(self.penSize2)
        self.sizeButtonGroup.addButton(self.penSize3)
        self.sizeButtonGroup.buttonClicked.connect(self.sizeButtonToggled)

        self.penSizeLayout.addWidget(self.penSize1)
        self.penSizeLayout.addWidget(self.penSize2)
        self.penSizeLayout.addWidget(self.penSize3)

        self.penSizeLayout.setSpacing(5)
        self.penSizeLayout.setContentsMargins(0, 0, 0, 0)

    def initPenColorButtons(self):
        self.colorSet = QWidget(self)
        self.colorLayout = QHBoxLayout()
        self.colorLayout.setSpacing(5)
        self.colorLayout.setContentsMargins(5, 0, 5, 0)
        self.colorSet.setLayout(self.colorLayout)

        self.presentColor = QPushButton(self.colorSet)
        self.presentColor.setFixedSize(self.iconWidth, self.iconHeight)
        self.presentColor.setEnabled(False)

        # adjust pen color

        self.colorPick = QWidget(self.colorSet)
        self.colorGrid = QGridLayout()
        self.colorGrid.setSpacing(0)
        self.colorGrid.setContentsMargins(5, 0, 5, 0)
        self.colorPick.setLayout(self.colorGrid)

        self.colorList = [('white'       ,       '#ffffff'),
                          ('red'         ,       '#ff0000'),
                          ('green'       ,       '#00ff00'),
                          ('blue'        ,       '#0000ff'),
                          ('cyan'        ,       '#00ffff'),
                          ('magenta'     ,       '#ff00ff'),
                          ('yellow'      ,       '#ffff00'),
                          ('gray'        ,       '#a0a0a4'),

                          ('black'       ,       '#000000'),
                          ('darkRed'     ,       '#800000'),
                          ('darkGreen'   ,       '#008000'),
                          ('darkBlue'    ,       '#000080'),
                          ('darkCyan'    ,       '#008080'),
                          ('darkMagenta' ,       '#800080'),
                          ('darkYellow'  ,       '#808000'),
                          ('darkGray'    ,       '#808080')]

        self.generateButtons()

        self.colorButtonGroup = QButtonGroup(self)
        for button in self.colorButtons:
            self.colorButtonGroup.addButton(button)
        self.colorButtonGroup.buttonClicked.connect(self.colorButtonToggled)

        # set the layout
        tmp = 0
        for x in range(0, 2):
            for y in range(0, int(len(self.colorList) / 2)):
                self.colorGrid.addWidget(self.colorButtons[tmp], x, y)
                tmp += 1

        self.colorGrid.setSpacing(0)
        self.colorGrid.setContentsMargins(0, 0, 0, 0)

        self.colorLayout.addWidget(self.presentColor)
        self.colorLayout.addWidget(self.colorPick)

    def initFontWidget(self):
        self.fontDialog = QFontDialog()
        self.changeFontButton = QPushButton(self)
        self.fontDialog.setCurrentFont(QFont('Sans serif'))
        self.changeFontButton.setText('{0} {1}'.format(self.fontDialog.currentFont().family(),
                                                       self.fontDialog.currentFont().pointSize()))
        self.changeFontButton.clicked.connect(self.fontButtonClicked)

    def showFontWidget(self):
        self.changeFontButton.show()
        self.penSize1.hide()
        self.penSize2.hide()
        self.penSize3.hide()

    def showPenWidget(self):
        self.changeFontButton.hide()
        self.penSize1.show()
        self.penSize2.show()
        self.penSize3.show()

    # slots
    def colorButtonToggled(self, button):
        self.presentColor.setStyleSheet('QPushButton { background-color: %s; }' % button.objectName())
        self.penColorTrigger.emit(button.objectName())

    def sizeButtonToggled(self, button):
        self.penSizeTrigger.emit(int(button.objectName()) * 2)

    def fontButtonClicked(self):
        ok = True
        font = QFontDialog.getFont(self)
        if font[1]:
            self.changeFontButton.setText('{0} {1}'.format(font[0].family(),
                                                           font[0].pointSize()))
            self.fontChangeTrigger.emit(font[0])
