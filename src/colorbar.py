from PyQt5.Qt import *
from sys import argv
from constant import *


class PenSetWidget(QWidget):
    def __init__(self, parent=None):
        super(PenSetWidget, self).__init__(parent)

        self.setWindowFlags(Qt.ToolTip)

        self.paddingX = 5
        self.paddingY = 2
        self.iconWidth = self.iconHeight = 28

        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(5, 0, 5, 0)

        # adjust pen size
        self.penSize1 = QPushButton('1', self)
        self.penSize1.setObjectName('1')
        self.penSize1.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize1.setCheckable(True)

        self.penSize2 = QPushButton('2', self)
        self.penSize2.setObjectName('2')
        self.penSize2.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize2.setCheckable(True)

        self.penSize3 = QPushButton('3', self)
        self.penSize3.setObjectName('3')
        self.penSize3.setFixedSize(self.iconWidth, self.iconHeight)
        self.penSize3.setCheckable(True)

        self.sizeButtonGroup = QButtonGroup(self)
        self.sizeButtonGroup.addButton(self.penSize1)
        self.sizeButtonGroup.addButton(self.penSize2)
        self.sizeButtonGroup.addButton(self.penSize3)
        self.sizeButtonGroup.buttonClicked.connect(self.sizeButtonToggled)

        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.VLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.mainLayout.addWidget(self.penSize1)
        self.mainLayout.addWidget(self.penSize2)
        self.mainLayout.addWidget(self.penSize3)
        self.mainLayout.addWidget(self.separator)

        self.colorSet = QWidget(self)
        self.colorLayout = QHBoxLayout()
        self.colorLayout.setSpacing(5)
        self.colorLayout.setContentsMargins(5, 0, 5, 0)
        self.colorSet.setLayout(self.colorLayout)

        self.presentColor = QPushButton('P', self.colorSet)
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

        tmp = 0
        for x in range(0, 2):
            for y in range(0, len(self.colorList) / 2):
                self.colorGrid.addWidget(self.colorButtons[tmp], x, y)
                tmp += 1

        self.colorGrid.setSpacing(0)
        self.colorGrid.setContentsMargins(0, 0, 0, 0)

        self.colorLayout.addWidget(self.presentColor)
        self.colorLayout.addWidget(self.colorPick)
        self.mainLayout.addWidget(self.colorSet)

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
            button.toggled.connect(self.colorButtonToggled)
            self.colorButtons.append(button)

    def colorButtonToggled(self):
        self.sender().setChecked(False)

        colorNow = None
        button = self.sender()
        for color in self.colorList:
            if button.objectName() == color[0]:
                colorNow = color[1]
                break
        self.presentColor.setStyleSheet('QPushButton { background-color: %s; }' % colorNow)

        if self.parent is not None:
            self.parent().penColorNow = colorNow

    def sizeButtonToggled(self, button):
        if self.parent() is not None:
            self.parent().penSizeNow = button.objectName()


if __name__ == '__main__':
    a = QApplication(argv)

    test = PenSetWidget()
    test.show()

    a.exec_()
