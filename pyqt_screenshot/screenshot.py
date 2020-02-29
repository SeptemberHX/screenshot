#!/usr/bin/python3
from PyQt5.QtCore import QRect, QPoint, QRectF, QSize, QLineF, QPointF, QEventLoop
from PyQt5.QtGui import QColor, QPainterPath, QKeySequence, QGuiApplication, QPixmap, QPen, QBrush, QImage, QPainter, \
    QPolygonF, QClipboard, QCursor, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView, QApplication, QGraphicsScene, QShortcut, QFileDialog, QDialog

from pyqt_screenshot.toolbar import *
from pyqt_screenshot.colorbar import *
from pyqt_screenshot.textinput import *

from math import *

qtApp = None


class Screenshot(QGraphicsView):
    """ Main Class """

    screen_shot_grabed = pyqtSignal(QImage)
    widget_closed = pyqtSignal()

    def __init__(self, flags=constant.DEFAULT, parent=None):
        """
        flags: binary flags. see the flags in the constant.py
        """
        super().__init__(parent)

        # Init
        self.penColorNow = QColor(PENCOLOR)
        self.penSizeNow = PENSIZE
        self.fontNow = QFont('Sans')
        self.clipboard = QApplication.clipboard()

        self.drawListResult = []  # draw list that sure to be drew, [action, coord]
        self.drawListProcess = None  # the process to the result
        self.selectedArea = QRect()  # a QRect instance which stands for the selected area
        self.selectedAreaRaw = QRect()
        self.mousePosition = MousePosition.OUTSIDE_AREA  # mouse position
        self.screenPixel = None
        self.textRect = None

        self.mousePressed = False
        self.action = ACTION_SELECT
        self.mousePoint = self.cursor().pos()

        self.startX, self.startY = 0, 0  # the point where you start
        self.endX, self.endY = 0, 0  # the point where you end
        self.pointPath = QPainterPath()  # the point mouse passes, used by draw free line
        self.itemsToRemove = []  # the items that should not draw on screenshot picture
        self.textPosition = None

        # result
        self.target_img = None

        # Init window
        self.getscreenshot()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QGraphicsView { border-style: none; }")

        self.tooBar = MyToolBar(flags, self)
        self.tooBar.trigger.connect(self.changeAction)

        self.penSetBar = None
        if flags & constant.RECT or flags & constant.ELLIPSE or flags & constant.LINE or flags & constant.FREEPEN \
                or flags & constant.ARROW or flags & constant.TEXT:
            self.penSetBar = PenSetWidget(self)
            self.penSetBar.penSizeTrigger.connect(self.changePenSize)
            self.penSetBar.penColorTrigger.connect(self.changePenColor)
            self.penSetBar.fontChangeTrigger.connect(self.changeFont)

        self.textInput = TextInput(self)
        self.textInput.inputChanged.connect(self.textChange)
        self.textInput.cancelPressed.connect(self.cancelInput)
        self.textInput.okPressed.connect(self.okInput)

        print('======>>> {0}, {1}'.format(self.screenPixel.width(), self.screenPixel.height()))
        self.graphicsScene = QGraphicsScene(0, 0, self.screenPixel.width(), self.screenPixel.height())

        self.show()
        self.setScene(self.graphicsScene)
        self.windowHandle().setScreen(QGuiApplication.screenAt(QCursor.pos()))
        self.scale = self.get_scale()
        # self.setFixedSize(self.screenPixel.width(), self.screenPixel.height())
        self.setGeometry(QGuiApplication.screenAt(QCursor.pos()).geometry())
        self.showFullScreen()
        self.redraw()

        QShortcut(QKeySequence('ctrl+s'), self).activated.connect(self.saveScreenshot)
        QShortcut(QKeySequence('esc'), self).activated.connect(self.close)

    @staticmethod
    def take_screenshot(flags):
        loop = QEventLoop()
        screen_shot = Screenshot(flags)
        screen_shot.show()
        screen_shot.widget_closed.connect(loop.quit)

        loop.exec()
        img = screen_shot.target_img
        return img

    def getscreenshot(self):
        screen = QGuiApplication.screenAt(QCursor.pos())
        self.screenPixel = screen.grabWindow(0)

    def mousePressEvent(self, event):
        """
        :type event: QMouseEvent
        :param event:
        :return:
        """
        if event.button() != Qt.LeftButton:
            return

        if self.action is None:
            self.action = ACTION_SELECT

        self.startX, self.startY = event.x(), event.y()

        if self.action == ACTION_SELECT:
            if self.mousePosition == MousePosition.OUTSIDE_AREA:
                self.mousePressed = True
                self.selectedArea = QRect()
                self.selectedArea.setTopLeft(QPoint(event.x(), event.y()))
                self.selectedArea.setBottomRight(QPoint(event.x(), event.y()))
                self.redraw()
            elif self.mousePosition == MousePosition.INSIDE_AREA:
                self.mousePressed = True
            else:
                pass
        elif self.action == ACTION_MOVE_SELECTED:
            if self.mousePosition == MousePosition.OUTSIDE_AREA:
                self.action = ACTION_SELECT
                self.selectedArea = QRect()
                self.selectedArea.setTopLeft(QPoint(event.x(), event.y()))
                self.selectedArea.setBottomRight(QPoint(event.x(), event.y()))
                self.redraw()
            self.mousePressed = True
        elif self.action in DRAW_ACTION:
            self.mousePressed = True
            if self.action == ACTION_FREEPEN:
                self.pointPath = QPainterPath()
                self.pointPath.moveTo(QPoint(event.x(), event.y()))
            elif self.action == ACTION_TEXT:
                if self.textPosition is None:
                    self.textPosition = QPoint(event.x(), event.y())
                    self.textRect = None
                    self.redraw()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        :type event: QMouseEvent
        :param event:
        :return:
        """
        self.mousePoint = QPoint(event.globalPos().x(), event.globalPos().y())

        if self.action is None:
            self.action = ACTION_SELECT

        if not self.mousePressed:
            point = QPoint(event.x(), event.y())
            self.detectMousePosition(point)
            self.setCursorStyle()
            self.redraw()
        else:
            self.endX, self.endY = event.x(), event.y()

            # if self.mousePosition != OUTSIDE_AREA:
            #    self.action = ACTION_MOVE_SELECTED

            if self.action == ACTION_SELECT:
                self.selectedArea.setBottomRight(QPoint(event.x(), event.y()))
                self.redraw()
            elif self.action == ACTION_MOVE_SELECTED:
                self.selectedArea = QRect(self.selectedAreaRaw)

                if self.mousePosition == MousePosition.INSIDE_AREA:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    if 0 <= moveToX <= self.screenPixel.width() - 1 - self.selectedArea.width():
                        self.selectedArea.moveLeft(moveToX)
                    if 0 <= moveToY <= self.screenPixel.height() - 1 - self.selectedArea.height():
                        self.selectedArea.moveTop(moveToY)
                    self.selectedArea = self.selectedArea.normalized()
                    self.selectedAreaRaw = QRect(self.selectedArea)
                    self.startX, self.startY = event.x(), event.y()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_LEFT_SIDE:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    if moveToX <= self.selectedArea.right():
                        self.selectedArea.setLeft(moveToX)
                        self.selectedArea = self.selectedArea.normalized()
                        self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_RIGHT_SIDE:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    self.selectedArea.setRight(moveToX)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_UP_SIDE:
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTop(moveToY)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_DOWN_SIDE:
                    moveToY = event.y() - self.startY + self.selectedArea.bottom()
                    self.selectedArea.setBottom(moveToY)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_TOP_LEFT_CORNER:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTopLeft(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_BOTTOM_RIGHT_CORNER:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    moveToY = event.y() - self.startY + self.selectedArea.bottom()
                    self.selectedArea.setBottomRight(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_TOP_RIGHT_CORNER:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTopRight(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == MousePosition.ON_THE_BOTTOM_LEFT_CORNER:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    moveToY = event.y() - self.startY + self.selectedArea.bottom()
                    self.selectedArea.setBottomLeft(QPoint(moveToX, moveToY))
                    self.redraw()
                else:
                    pass
            elif self.action == ACTION_RECT:
                self.drawRect(self.startX, self.startY, event.x(), event.y(), False)
                self.redraw()
                pass
            elif self.action == ACTION_ELLIPSE:
                self.drawEllipse(self.startX, self.startY, event.x(), event.y(), False)
                self.redraw()
            elif self.action == ACTION_ARROW:
                self.drawArrow(self.startX, self.startY, event.x(), event.y(), False)
                self.redraw()
            elif self.action == ACTION_LINE:
                self.drawLine(self.startX, self.startY, event.x(), event.y(), False)
                self.redraw()
            elif self.action == ACTION_FREEPEN:
                y1, y2 = event.x(), event.y()
                rect = self.selectedArea.normalized()
                if y1 <= rect.left():
                    y1 = rect.left()
                elif y1 >= rect.right():
                    y1 = rect.right()

                if y2 <= rect.top():
                    y2 = rect.top()
                elif y2 >= rect.bottom():
                    y2 = rect.bottom()

                self.pointPath.lineTo(y1, y2)
                self.drawFreeLine(self.pointPath, False)
                self.redraw()

    def mouseReleaseEvent(self, event):
        """
        :type event: QMouseEvent
        :param event:
        :return:
        """
        if event.button() != Qt.LeftButton:
            return

        if self.mousePressed:
            self.mousePressed = False
            self.endX, self.endY = event.x(), event.y()

            if self.action == ACTION_SELECT:
                self.selectedArea.setBottomRight(QPoint(event.x(), event.y()))
                self.selectedAreaRaw = QRect(self.selectedArea)
                self.action = ACTION_MOVE_SELECTED
                self.redraw()
            elif self.action == ACTION_MOVE_SELECTED:
                self.selectedAreaRaw = QRect(self.selectedArea)
                self.redraw()
                # self.action = None
            elif self.action == ACTION_RECT:
                self.drawRect(self.startX, self.startY, event.x(), event.y(), True)
                self.redraw()
            elif self.action == ACTION_ELLIPSE:
                self.drawEllipse(self.startX, self.startY, event.x(), event.y(), True)
                self.redraw()
            elif self.action == ACTION_ARROW:
                self.drawArrow(self.startX, self.startY, event.x(), event.y(), True)
                self.redraw()
            elif self.action == ACTION_LINE:
                self.drawLine(self.startX, self.startY, event.x(), event.y(), True)
                self.redraw()
            elif self.action == ACTION_FREEPEN:
                self.drawFreeLine(self.pointPath, True)
                self.redraw()

    def detectMousePosition(self, point):
        """
        :type point: QPoint
        :param point: the mouse position you want to check
        :return:
        """
        if self.selectedArea == QRect():
            self.mousePosition = MousePosition.OUTSIDE_AREA
            return

        if self.selectedArea.left() - ERRORRANGE <= point.x() <= self.selectedArea.left() and (
                            self.selectedArea.top() - ERRORRANGE <= point.y() <= self.selectedArea.top()):
            self.mousePosition = MousePosition.ON_THE_TOP_LEFT_CORNER
        elif self.selectedArea.right() <= point.x() <= self.selectedArea.right() + ERRORRANGE and (
                            self.selectedArea.top() - ERRORRANGE <= point.y() <= self.selectedArea.top()):
            self.mousePosition = MousePosition.ON_THE_TOP_RIGHT_CORNER
        elif self.selectedArea.left() - ERRORRANGE <= point.x() <= self.selectedArea.left() and (
                        self.selectedArea.bottom() <= point.y() <= self.selectedArea.bottom() + ERRORRANGE):
            self.mousePosition = MousePosition.ON_THE_BOTTOM_LEFT_CORNER
        elif self.selectedArea.right() <= point.x() <= self.selectedArea.right() + ERRORRANGE and (
                        self.selectedArea.bottom() <= point.y() <= self.selectedArea.bottom() + ERRORRANGE):
            self.mousePosition = MousePosition.ON_THE_BOTTOM_RIGHT_CORNER
        elif -ERRORRANGE <= point.x() - self.selectedArea.left() <= 0 and (
                        self.selectedArea.topLeft().y() < point.y() < self.selectedArea.bottomLeft().y()):
            self.mousePosition = MousePosition.ON_THE_LEFT_SIDE
        elif 0 <= point.x() - self.selectedArea.right() <= ERRORRANGE and (
                        self.selectedArea.topRight().y() < point.y() < self.selectedArea.bottomRight().y()):
            self.mousePosition = MousePosition.ON_THE_RIGHT_SIDE
        elif -ERRORRANGE <= point.y() - self.selectedArea.top() <= 0 and (
                        self.selectedArea.topLeft().x() < point.x() < self.selectedArea.topRight().x()):
            self.mousePosition = MousePosition.ON_THE_UP_SIDE
        elif 0 <= point.y() - self.selectedArea.bottom() <= ERRORRANGE and (
                        self.selectedArea.bottomLeft().x() < point.x() < self.selectedArea.bottomRight().x()):
            self.mousePosition = MousePosition.ON_THE_DOWN_SIDE
        elif not self.selectedArea.contains(point):
            self.mousePosition = MousePosition.OUTSIDE_AREA
        else:
            self.mousePosition = MousePosition.INSIDE_AREA

    def setCursorStyle(self):
        if self.action in DRAW_ACTION:
            self.setCursor(Qt.CrossCursor)
            return

        if self.mousePosition == MousePosition.ON_THE_LEFT_SIDE or \
                        self.mousePosition == MousePosition.ON_THE_RIGHT_SIDE:

            self.setCursor(Qt.SizeHorCursor)
        elif self.mousePosition == MousePosition.ON_THE_UP_SIDE or \
                        self.mousePosition == MousePosition.ON_THE_DOWN_SIDE:

            self.setCursor(Qt.SizeVerCursor)
        elif self.mousePosition == MousePosition.ON_THE_TOP_LEFT_CORNER or \
                        self.mousePosition == MousePosition.ON_THE_BOTTOM_RIGHT_CORNER:

            self.setCursor(Qt.SizeFDiagCursor)
        elif self.mousePosition == MousePosition.ON_THE_TOP_RIGHT_CORNER or \
                        self.mousePosition == MousePosition.ON_THE_BOTTOM_LEFT_CORNER:

            self.setCursor(Qt.SizeBDiagCursor)
        elif self.mousePosition == MousePosition.OUTSIDE_AREA:
            self.setCursor(Qt.ArrowCursor)
        elif self.mousePosition == MousePosition.INSIDE_AREA:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            pass

    def drawMagnifier(self):
        # First, calculate the magnifier position due to the mouse position
        watchAreaWidth = 16
        watchAreaHeight = 16
        watchAreaPixmap = QPixmap()

        cursor_pos = self.mousePoint

        watchArea = QRect(QPoint(cursor_pos.x() - watchAreaWidth / 2, cursor_pos.y() - watchAreaHeight / 2),
                          QPoint(cursor_pos.x() + watchAreaWidth / 2, cursor_pos.y() + watchAreaHeight / 2))
        if watchArea.left() < 0:
            watchArea.moveLeft(0)
            watchArea.moveRight(watchAreaWidth)
        if self.mousePoint.x() + watchAreaWidth / 2 >= self.screenPixel.width():
            watchArea.moveRight(self.screenPixel.width() - 1)
            watchArea.moveLeft(watchArea.right() - watchAreaWidth)
        if self.mousePoint.y() - watchAreaHeight / 2 < 0:
            watchArea.moveTop(0)
            watchArea.moveBottom(watchAreaHeight)
        if self.mousePoint.y() + watchAreaHeight / 2 >= self.screenPixel.height():
            watchArea.moveBottom(self.screenPixel.height() - 1)
            watchArea.moveTop(watchArea.bottom() - watchAreaHeight)

        # tricks to solve the hidpi impact on QCursor.pos()
        watchArea.setTopLeft(QPoint(watchArea.topLeft().x() * self.scale, watchArea.topLeft().y() * self.scale))
        watchArea.setBottomRight(QPoint(watchArea.bottomRight().x() * self.scale, watchArea.bottomRight().y() * self.scale))
        watchAreaPixmap = self.screenPixel.copy(watchArea)

        # second, calculate the magnifier area
        magnifierAreaWidth = watchAreaWidth * 10
        magnifierAreaHeight = watchAreaHeight * 10
        fontAreaHeight = 40

        cursorSize = 24
        magnifierArea = QRectF(QPoint(QCursor.pos().x() + cursorSize, QCursor.pos().y() + cursorSize),
                               QPoint(QCursor.pos().x() + cursorSize + magnifierAreaWidth,
                                      QCursor.pos().y() + cursorSize + magnifierAreaHeight))
        if magnifierArea.right() >= self.screenPixel.width():
            magnifierArea.moveLeft(QCursor.pos().x() - magnifierAreaWidth - cursorSize / 2)
        if magnifierArea.bottom() + fontAreaHeight >= self.screenPixel.height():
            magnifierArea.moveTop(QCursor.pos().y() - magnifierAreaHeight - cursorSize / 2 - fontAreaHeight)

        # third, draw the watch area to magnifier area
        watchAreaScaled = watchAreaPixmap.scaled(QSize(magnifierAreaWidth * self.scale, magnifierAreaHeight * self.scale))
        magnifierPixmap = self.graphicsScene.addPixmap(watchAreaScaled)
        magnifierPixmap.setOffset(magnifierArea.topLeft())

        # then draw lines and text
        self.graphicsScene.addRect(QRectF(magnifierArea), QPen(QColor(255, 255, 255), 2))
        self.graphicsScene.addLine(QLineF(QPointF(magnifierArea.center().x(), magnifierArea.top()),
                                          QPointF(magnifierArea.center().x(), magnifierArea.bottom())),
                                   QPen(QColor(0, 255, 255), 2))
        self.graphicsScene.addLine(QLineF(QPointF(magnifierArea.left(), magnifierArea.center().y()),
                                          QPointF(magnifierArea.right(), magnifierArea.center().y())),
                                   QPen(QColor(0, 255, 255), 2))

        # get the rgb of mouse point
        pointRgb = QColor(self.screenPixel.toImage().pixel(self.mousePoint))

        # draw information
        self.graphicsScene.addRect(QRectF(magnifierArea.bottomLeft(),
                                          magnifierArea.bottomRight() + QPoint(0, fontAreaHeight + 30)),
                                   Qt.black,
                                   QBrush(Qt.black))
        rgbInfo = self.graphicsScene.addSimpleText(
            ' Rgb: ({0}, {1}, {2})'.format(pointRgb.red(), pointRgb.green(), pointRgb.blue()))
        rgbInfo.setPos(magnifierArea.bottomLeft() + QPoint(0, 5))
        rgbInfo.setPen(QPen(QColor(255, 255, 255), 2))

        rect = self.selectedArea.normalized()
        sizeInfo = self.graphicsScene.addSimpleText(' Size: {0} x {1}'.format(rect.width() * self.scale, rect.height() * self.scale))
        sizeInfo.setPos(magnifierArea.bottomLeft() + QPoint(0, 15) + QPoint(0, fontAreaHeight / 2))
        sizeInfo.setPen(QPen(QColor(255, 255, 255), 2))

    def get_scale(self):
        # tricks to solve the hidpi impact on QCursor.pos()
        screen = QGuiApplication.screenAt(QCursor.pos())
        scale = self.screenPixel.width() // screen.geometry().width()
        return scale

    def saveScreenshot(self, clipboard=False, fileName='screenshot.png', picType='png'):
        fullWindow = QRect(0, 0, self.width() - 1, self.height() - 1)
        selected = QRect(self.selectedArea)
        if selected.left() < 0:
            selected.setLeft(0)
        if selected.right() >= self.width():
            selected.setRight(self.width() - 1)
        if selected.top() < 0:
            selected.setTop(0)
        if selected.bottom() >= self.height():
            selected.setBottom(self.height() - 1)

        source = (fullWindow & selected)
        source.setTopLeft(QPoint(source.topLeft().x() * self.scale, source.topLeft().y() * self.scale))
        source.setBottomRight(QPoint(source.bottomRight().x() * self.scale, source.bottomRight().y() * self.scale))
        image = self.screenPixel.copy(source)

        if clipboard:
            QGuiApplication.clipboard().setImage(image, QClipboard.Clipboard)
        else:
            image.save(fileName, picType, 10)
        self.target_img = image
        self.screen_shot_grabed.emit(QImage(image))

    def redraw(self):
        self.graphicsScene.clear()

        # draw screenshot
        self.graphicsScene.addPixmap(self.screenPixel)

        # prepare for drawing selected area
        rect = QRectF(self.selectedArea)
        rect = rect.normalized()

        topLeftPoint = rect.topLeft()
        topRightPoint = rect.topRight()
        bottomLeftPoint = rect.bottomLeft()
        bottomRightPoint = rect.bottomRight()
        topMiddlePoint = (topLeftPoint + topRightPoint) / 2
        leftMiddlePoint = (topLeftPoint + bottomLeftPoint) / 2
        bottomMiddlePoint = (bottomLeftPoint + bottomRightPoint) / 2
        rightMiddlePoint = (topRightPoint + bottomRightPoint) / 2

        # draw the picture mask
        mask = QColor(0, 0, 0, 155)

        if self.selectedArea == QRect():
            self.graphicsScene.addRect(0, 0, self.screenPixel.width(), self.screenPixel.height(), QPen(Qt.NoPen), mask)
        else:
            self.graphicsScene.addRect(0, 0, self.screenPixel.width(), topRightPoint.y(), QPen(Qt.NoPen), mask)
            self.graphicsScene.addRect(0, topLeftPoint.y(), topLeftPoint.x(), rect.height(), QPen(Qt.NoPen), mask)
            self.graphicsScene.addRect(topRightPoint.x(), topRightPoint.y(),
                                       self.screenPixel.width() - topRightPoint.x(),
                                       rect.height(),
                                       QPen(Qt.NoPen),
                                       mask)
            self.graphicsScene.addRect(0, bottomLeftPoint.y(),
                                       self.screenPixel.width(), self.screenPixel.height() - bottomLeftPoint.y(),
                                       QPen(Qt.NoPen), mask)

        # draw the toolBar
        if self.action != ACTION_SELECT:
            spacing = 5
            # show the toolbar first, then move it to the correct position
            # because the width of it may be wrong if this is the first time it shows
            self.tooBar.show()

            dest = QPointF(rect.bottomRight() - QPointF(self.tooBar.width(), 0) - QPointF(spacing, -spacing))
            if dest.x() < spacing:
                dest.setX(spacing)
            pen_set_bar_height = self.penSetBar.height() if self.penSetBar is not None else 0
            if dest.y() + self.tooBar.height() + pen_set_bar_height >= self.height():
                if rect.top() - self.tooBar.height() - pen_set_bar_height < spacing:
                    dest.setY(rect.top() + spacing)
                else:
                    dest.setY(rect.top() - self.tooBar.height() - pen_set_bar_height - spacing)

            self.tooBar.move(dest.toPoint())

            if self.penSetBar is not None:
                self.penSetBar.show()
                self.penSetBar.move(dest.toPoint() + QPoint(0, self.tooBar.height() + spacing))

                if self.action == ACTION_TEXT:
                    self.penSetBar.showFontWidget()
                else:
                    self.penSetBar.showPenWidget()
        else:
            self.tooBar.hide()

            if self.penSetBar is not None:
                self.penSetBar.hide()

        # draw the list
        for step in self.drawListResult:
            self.drawOneStep(step)

        if self.drawListProcess is not None:
            self.drawOneStep(self.drawListProcess)
            if self.action != ACTION_TEXT:
                self.drawListProcess = None

        if self.selectedArea != QRect():
            self.itemsToRemove = []

            # draw the selected rectangle
            pen = QPen(QColor(0, 255, 255), 2)
            self.itemsToRemove.append(self.graphicsScene.addRect(rect, pen))

            # draw the drag point
            radius = QPoint(3, 3)
            brush = QBrush(QColor(0, 255, 255))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(topLeftPoint - radius, topLeftPoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(topMiddlePoint - radius, topMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(topRightPoint - radius, topRightPoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(leftMiddlePoint - radius, leftMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(rightMiddlePoint - radius, rightMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(bottomLeftPoint - radius, bottomLeftPoint + radius), pen, brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(bottomMiddlePoint - radius, bottomMiddlePoint + radius), pen,
                                              brush))
            self.itemsToRemove.append(
                self.graphicsScene.addEllipse(QRectF(bottomRightPoint - radius, bottomRightPoint + radius), pen, brush))

        # draw the textedit
        if self.textPosition is not None:
            textSpacing = 50
            position = QPoint()
            if self.textPosition.x() + self.textInput.width() >= self.screenPixel.width():
                position.setX(self.textPosition.x() - self.textInput.width())
            else:
                position.setX(self.textPosition.x())

            if self.textRect is not None:
                if self.textPosition.y() + self.textInput.height() + self.textRect.height() >= self.screenPixel.height():
                    position.setY(self.textPosition.y() - self.textInput.height() - self.textRect.height())
                else:
                    position.setY(self.textPosition.y() + self.textRect.height())
            else:
                if self.textPosition.y() + self.textInput.height() >= self.screenPixel.height():
                    position.setY(self.textPosition.y() - self.textInput.height())
                else:
                    position.setY(self.textPosition.y())

            self.textInput.move(position)
            self.textInput.show()
            # self.textInput.getFocus()

        # draw the magnifier
        if self.action == ACTION_SELECT:
            self.drawMagnifier()
            if self.mousePressed:
                self.drawSizeInfo()

        if self.action == ACTION_MOVE_SELECTED:
            self.drawSizeInfo()

    # deal with every step in drawList
    def drawOneStep(self, step):
        """
        :type step: tuple
        """
        if step[0] == ACTION_RECT:
            self.graphicsScene.addRect(QRectF(QPointF(step[1], step[2]),
                                              QPointF(step[3], step[4])), step[5])
        elif step[0] == ACTION_ELLIPSE:
            self.graphicsScene.addEllipse(QRectF(QPointF(step[1], step[2]),
                                                 QPointF(step[3], step[4])), step[5])
        elif step[0] == ACTION_ARROW:
            arrow = QPolygonF()

            linex = float(step[1] - step[3])
            liney = float(step[2] - step[4])
            line = sqrt(pow(linex, 2) + pow(liney, 2))

            # in case to divided by 0
            if line == 0:
                return

            sinAngel = liney / line
            cosAngel = linex / line

            # sideLength is the length of bottom side of the body of an arrow
            # arrowSize is the size of the head of an arrow, left and right
            # sides' size is arrowSize, and the bottom side's size is arrowSize / 2
            sideLength = step[5].width()
            arrowSize = 8
            bottomSize = arrowSize / 2

            tmpPoint = QPointF(step[3] + arrowSize * sideLength * cosAngel, step[4] + arrowSize * sideLength * sinAngel)

            point1 = QPointF(step[1] + sideLength * sinAngel, step[2] - sideLength * cosAngel)
            point2 = QPointF(step[1] - sideLength * sinAngel, step[2] + sideLength * cosAngel)
            point3 = QPointF(tmpPoint.x() - sideLength * sinAngel, tmpPoint.y() + sideLength * cosAngel)
            point4 = QPointF(tmpPoint.x() - bottomSize * sideLength * sinAngel,
                             tmpPoint.y() + bottomSize * sideLength * cosAngel)
            point5 = QPointF(step[3], step[4])
            point6 = QPointF(tmpPoint.x() + bottomSize * sideLength * sinAngel,
                             tmpPoint.y() - bottomSize * sideLength * cosAngel)
            point7 = QPointF(tmpPoint.x() + sideLength * sinAngel, tmpPoint.y() - sideLength * cosAngel)

            arrow.append(point1)
            arrow.append(point2)
            arrow.append(point3)
            arrow.append(point4)
            arrow.append(point5)
            arrow.append(point6)
            arrow.append(point7)
            arrow.append(point1)

            self.graphicsScene.addPolygon(arrow, step[5], step[6])
        elif step[0] == ACTION_LINE:
            self.graphicsScene.addLine(QLineF(QPointF(step[1], step[2]), QPointF(step[3], step[4])), step[5])
        elif step[0] == ACTION_FREEPEN:
            self.graphicsScene.addPath(step[1], step[2])
        elif step[0] == ACTION_TEXT:
            textAdd = self.graphicsScene.addSimpleText(step[1], step[2])
            textAdd.setPos(step[3])
            textAdd.setBrush(QBrush(step[4]))
            self.textRect = textAdd.boundingRect()

    # draw the size information on the top left corner
    def drawSizeInfo(self):
        sizeInfoAreaWidth = 200
        sizeInfoAreaHeight = 30
        spacing = 5
        rect = self.selectedArea.normalized()
        sizeInfoArea = QRect(rect.left(), rect.top() - spacing - sizeInfoAreaHeight,
                             sizeInfoAreaWidth, sizeInfoAreaHeight)

        if sizeInfoArea.top() < 0:
            sizeInfoArea.moveTopLeft(rect.topLeft() + QPoint(spacing, spacing))
        if sizeInfoArea.right() >= self.screenPixel.width():
            sizeInfoArea.moveTopLeft(rect.topLeft() - QPoint(spacing, spacing) - QPoint(sizeInfoAreaWidth, 0))
        if sizeInfoArea.left() < spacing:
            sizeInfoArea.moveLeft(spacing)
        if sizeInfoArea.top() < spacing:
            sizeInfoArea.moveTop(spacing)

        self.itemsToRemove.append(self.graphicsScene.addRect(QRectF(sizeInfoArea), Qt.white, QBrush(Qt.black)))

        sizeInfo = self.graphicsScene.addSimpleText('  {0} x {1}'.format(rect.width() * self.scale, rect.height() * self.scale))
        sizeInfo.setPos(sizeInfoArea.topLeft() + QPoint(0, 2))
        sizeInfo.setPen(QPen(QColor(255, 255, 255), 2))
        self.itemsToRemove.append(sizeInfo)

    def drawRect(self, x1, x2, y1, y2, result):
        rect = self.selectedArea.normalized()
        tmpRect = QRect(QPoint(x1, x2), QPoint(y1, y2)).normalized()
        resultRect = rect & tmpRect
        tmp = [ACTION_RECT, resultRect.topLeft().x(), resultRect.topLeft().y(),
               resultRect.bottomRight().x(), resultRect.bottomRight().y(),
               QPen(QColor(self.penColorNow), int(self.penSizeNow))]
        if result:
            self.drawListResult.append(tmp)
        else:
            self.drawListProcess = tmp

    def drawEllipse(self, x1, x2, y1, y2, result):
        rect = self.selectedArea.normalized()
        tmpRect = QRect(QPoint(x1, x2), QPoint(y1, y2)).normalized()
        resultRect = rect & tmpRect
        tmp = [ACTION_ELLIPSE, resultRect.topLeft().x(), resultRect.topLeft().y(),
               resultRect.bottomRight().x(), resultRect.bottomRight().y(),
               QPen(QColor(self.penColorNow), int(self.penSizeNow))]
        if result:
            self.drawListResult.append(tmp)
        else:
            self.drawListProcess = tmp

    def drawArrow(self, x1, x2, y1, y2, result):
        rect = self.selectedArea.normalized()
        if y1 <= rect.left():
            y1 = rect.left()
        elif y1 >= rect.right():
            y1 = rect.right()

        if y2 <= rect.top():
            y2 = rect.top()
        elif y2 >= rect.bottom():
            y2 = rect.bottom()

        tmp = [ACTION_ARROW, x1, x2, y1, y2,
               QPen(QColor(self.penColorNow), int(self.penSizeNow)),
               QBrush(QColor(self.penColorNow))]
        if result:
            self.drawListResult.append(tmp)
        else:
            self.drawListProcess = tmp

    def drawLine(self, x1, x2, y1, y2, result):
        rect = self.selectedArea.normalized()
        if y1 <= rect.left():
            y1 = rect.left()
        elif y1 >= rect.right():
            y1 = rect.right()

        if y2 <= rect.top():
            y2 = rect.top()
        elif y2 >= rect.bottom():
            y2 = rect.bottom()

        tmp = [ACTION_LINE, x1, x2, y1, y2,
               QPen(QColor(self.penColorNow), int(self.penSizeNow))]
        if result:
            self.drawListResult.append(tmp)
        else:
            self.drawListProcess = tmp

    def drawFreeLine(self, pointPath, result):
        tmp = [ACTION_FREEPEN, QPainterPath(pointPath), QPen(QColor(self.penColorNow), int(self.penSizeNow))]
        if result:
            self.drawListResult.append(tmp)
        else:
            self.drawListProcess = tmp

    def textChange(self):
        if self.textPosition is None:
            return
        self.text = self.textInput.getText()
        self.drawListProcess = [ACTION_TEXT, str(self.text), QFont(self.fontNow), QPoint(self.textPosition),
                                QColor(self.penColorNow)]
        self.redraw()

    def undoOperation(self):
        if len(self.drawListResult) == 0:
            self.action = ACTION_SELECT
            self.selectedArea = QRect()
            self.selectedAreaRaw = QRect()
            self.tooBar.hide()
            if self.penSetBar is not None:
                self.penSetBar.hide()
        else:
            self.drawListResult.pop()
        self.redraw()

    def saveOperation(self):
        filename = QFileDialog.getSaveFileName(self, 'Save file', './screenshot.png', '*.png;;*.jpg')
        if len(filename[0]) == 0:
            return
        else:
            self.saveScreenshot(False, filename[0], filename[1][2:])
            self.close()

    def close(self):
        self.widget_closed.emit()
        super().close()
        self.tooBar.close()
        if self.penSetBar is not None:
            self.penSetBar.close()

    def saveToClipboard(self):
        QApplication.clipboard().setText('Test in save function')

        self.saveScreenshot(True)
        self.close()

    # slots
    def changeAction(self, nextAction):
        QApplication.clipboard().setText('Test in changeAction function')

        if nextAction == ACTION_UNDO:
            self.undoOperation()
        elif nextAction == ACTION_SAVE:
            self.saveOperation()
        elif nextAction == ACTION_CANCEL:
            self.close()
        elif nextAction == ACTION_SURE:
            self.saveToClipboard()

        else:
            self.action = nextAction

        self.setFocus()

    def changePenSize(self, nextPenSize):
        self.penSizeNow = nextPenSize

    def changePenColor(self, nextPenColor):
        self.penColorNow = nextPenColor

    def cancelInput(self):
        self.drawListProcess = None
        self.textPosition = None
        self.textRect = None
        self.textInput.hide()
        self.textInput.clearText()
        self.redraw()

    def okInput(self):
        self.text = self.textInput.getText()
        self.drawListResult.append(
            [ACTION_TEXT, str(self.text), QFont(self.fontNow), QPoint(self.textPosition), QColor(self.penColorNow)])
        self.textPosition = None
        self.textRect = None
        self.textInput.hide()
        self.textInput.clearText()
        self.redraw()

    def changeFont(self, font):
        self.fontNow = font
