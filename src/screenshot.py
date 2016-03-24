from PyQt5.Qt import *
import sys

from constant import *
from toolbar import *
from colorbar import *


class MainWindow(QGraphicsView):
    """ Main Class """

    def __init__(self):
        """ Init the main class """
        QWidget.__init__(self)

        # Init
        self.penColorNow = QColor(PENCOLOR)
        self.penSizeNow = PENSIZE

        self.drawListResult = []  # draw list that sure to be drew, [action, coord]
        self.drawListProcess = None  # the process to the result
        self.selectedArea = QRect()  # a QRect instance which stands for the selected area
        self.selectedAreaRaw = QRect()
        self.mousePosition = OUTSIDE_AREA  # mouse position
        self.screenPixel = None

        self.mousePressed = False
        self.action = ACTION_SELECT
        self.mousePoint = QPoint()

        self.startX, self.startY = 0, 0  # the point where you start
        self.endX, self.endY = 0, 0  # the point where you end

        self.itemsToRemove = []  # the items that should not draw on screenshot picture

        # Init window
        self.getscreenshot()

        self.showFullScreen()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QGraphicsView { border-style: none; }")

        self.tooBar = MyToolBar(self)
        self.tooBar.trigger.connect(self.changeAction)
        self.penSetBar = PenSetWidget(self)


        self.graphicsScene = QGraphicsScene(0, 0, self.screenPixel.width(), self.screenPixel.height())

        self.setScene(self.graphicsScene)
        self.redraw()

        QShortcut(QKeySequence('ctrl+s'), self).activated.connect(self.saveScreenshot)
        QShortcut(QKeySequence('esc'), self).activated.connect(self.close)

    def getscreenshot(self):
        screen = QGuiApplication.primaryScreen()
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
            if self.mousePosition == OUTSIDE_AREA:
                self.mousePressed = True

                self.selectedArea = QRect()
                self.selectedArea.setTopLeft(QPoint(event.x(), event.y()))
                self.selectedArea.setBottomRight(self.selectedArea.topLeft())
                self.redraw()
            elif self.mousePosition == INSIDE_AREA:
                self.mousePressed = True
            else:
                pass
        elif self.action == ACTION_MOVE_SELECTED:
            if self.mousePosition == OUTSIDE_AREA:
                self.action = ACTION_SELECT
            self.mousePressed = True
        elif self.action in DRAW_ACTION:
            self.mousePressed = True

    def mouseMoveEvent(self, event):
        """
        :type event: QMouseEvent
        :param event:
        :return:
        """
        self.mousePoint = QPoint(event.x(), event.y())
        if self.action is None:
            self.action = ACTION_SELECT

        if not self.mousePressed and self.action != ACTION_SELECT:
            point = QPoint(event.x(), event.y())
            self.detectMousePosition(point)
            self.setCursorStyle()

        if self.mousePressed:
            self.endX, self.endY = event.x(), event.y()

            # if self.mousePosition != OUTSIDE_AREA:
            #    self.action = ACTION_MOVE_SELECTED

            if self.action == ACTION_SELECT:
                self.selectedArea.setBottomRight(QPoint(event.x(), event.y()))
                self.redraw()
            elif self.action == ACTION_MOVE_SELECTED:
                self.selectedArea = QRect(self.selectedAreaRaw)
                if self.mousePosition == INSIDE_AREA:
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
                elif self.mousePosition == ON_THE_LEFT_SIDE:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    if moveToX <= self.selectedArea.right:
                        self.selectedArea.setLeft(moveToX)
                        self.selectedArea = self.selectedArea.normalized()
                        self.redraw()
                elif self.mousePosition == ON_THE_RIGHT_SIDE:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    self.selectedArea.setRight(moveToX)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_UP_SIDE:
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTop(moveToY)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_DOWN_SIDE:
                    moveToY = event.y() - self.startY + self.selectedArea.bottom()
                    self.selectedArea.setBottom(moveToY)
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_TOP_LEFT_CORNOR:
                    moveToX = event.x() - self.startX + self.selectedArea.left()
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTopLeft(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_BOTTOM_RIGHT_CORNOR:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    moveToY = event.y() - self.startY + self.selectedArea.bottom()
                    self.selectedArea.setBottomRight(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_TOP_RIGHT_CORNOR:
                    moveToX = event.x() - self.startX + self.selectedArea.right()
                    moveToY = event.y() - self.startY + self.selectedArea.top()
                    self.selectedArea.setTopRight(QPoint(moveToX, moveToY))
                    self.selectedArea = self.selectedArea.normalized()
                    self.redraw()
                elif self.mousePosition == ON_THE_BOTTOM_LEFT_CORNOR:
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
        else:
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
                print('In mouse move event')
                print(self.selectedArea.bottomRight())
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

    def detectMousePosition(self, point):
        """
        :type point: QPoint
        :param point: the mouse position you want to check
        :return:
        """
        if self.selectedArea == QRect():
            self.mousePosition = OUTSIDE_AREA
            return

        if self.selectedArea.left() - ERRORRANGE <= point.x() <= self.selectedArea.left() and (
                                self.selectedArea.top() - ERRORRANGE <= point.y() <= self.selectedArea.top()):
            self.mousePosition = ON_THE_TOP_LEFT_CORNOR
        elif self.selectedArea.right() <= point.x() <= self.selectedArea.right() + ERRORRANGE and (
                                self.selectedArea.top() - ERRORRANGE <= point.y() <= self.selectedArea.top()):
            self.mousePosition = ON_THE_TOP_RIGHT_CORNOR
        elif self.selectedArea.left() - ERRORRANGE <= point.x() <= self.selectedArea.left() and (
                                self.selectedArea.bottom() <= point.y() <= self.selectedArea.bottom() + ERRORRANGE):
            self.mousePosition = ON_THE_BOTTOM_LEFT_CORNOR
        elif self.selectedArea.right() <= point.x() <= self.selectedArea.right() + ERRORRANGE and (
                                self.selectedArea.bottom() <= point.y() <= self.selectedArea.bottom() + ERRORRANGE):
            self.mousePosition = ON_THE_BOTTOM_RIGHT_CORNOR
        elif -ERRORRANGE <= point.x() - self.selectedArea.left() <= 0 and (
                                self.selectedArea.topLeft().y() < point.y() < self.selectedArea.bottomLeft().y()):
            self.mousePosition = ON_THE_LEFT_SIDE
        elif 0 <= point.x() - self.selectedArea.right() <= ERRORRANGE and (
                                self.selectedArea.topRight().y() < point.y() < self.selectedArea.bottomRight().y()):
            self.mousePosition = ON_THE_RIGHT_SIDE
        elif -ERRORRANGE <= point.y() - self.selectedArea.top() <= 0 and (
                                self.selectedArea.topLeft().x() < point.x() < self.selectedArea.topRight().x()):
            self.mousePosition = ON_THE_UP_SIDE
        elif 0 <= point.y() - self.selectedArea.bottom() <= ERRORRANGE and (
                                self.selectedArea.bottomLeft().x() < point.x() < self.selectedArea.bottomRight().x()):
            self.mousePosition = ON_THE_DOWN_SIDE
        elif not self.selectedArea.contains(point):
            self.mousePosition = OUTSIDE_AREA
        else:
            self.mousePosition = INSIDE_AREA

    def setCursorStyle(self):
        if self.action in DRAW_ACTION:
            self.setCursor(Qt.CrossCursor)
            return

        if self.mousePosition == ON_THE_LEFT_SIDE or self.mousePosition == ON_THE_RIGHT_SIDE:
            self.setCursor(Qt.SizeHorCursor)
        elif self.mousePosition == ON_THE_UP_SIDE or self.mousePosition == ON_THE_DOWN_SIDE:
            self.setCursor(Qt.SizeVerCursor)
        elif self.mousePosition == ON_THE_TOP_LEFT_CORNOR or self.mousePosition == ON_THE_BOTTOM_RIGHT_CORNOR:
            self.setCursor(Qt.SizeFDiagCursor)
        elif self.mousePosition == ON_THE_TOP_RIGHT_CORNOR or self.mousePosition == ON_THE_BOTTOM_LEFT_CORNOR:
            self.setCursor(Qt.SizeBDiagCursor)
        elif self.mousePosition == OUTSIDE_AREA:
            self.setCursor(Qt.ArrowCursor)
        elif self.mousePosition == INSIDE_AREA:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            pass

    def drawMagnifier(self):
        # First, calculate the magnifier position due to the mouse position
        watchAreaWidth = 32
        watchAreaHeight = 28
        watchAreaPixmap = QPixmap()

        watchArea = QRect(QPoint(self.mousePoint.x() - watchAreaWidth / 2, self.mousePoint.y() - watchAreaHeight / 2),
                          QPoint(self.mousePoint.x() + watchAreaWidth / 2, self.mousePoint.y() + watchAreaHeight / 2))
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
        watchAreaPixmap = self.screenPixel.copy(watchArea)

        # second, calculate the magnifier area
        magnifierAreaWidth = watchAreaWidth * 5
        magnifierAreaHeight = watchAreaHeight * 5
        fontAreaHeight = 40

        cursorSize = 24
        magnifierArea = QRectF(QPoint(self.mousePoint.x() + cursorSize, self.mousePoint.y() + cursorSize),
                               QPoint(self.mousePoint.x() + cursorSize + magnifierAreaWidth,
                                      self.mousePoint.y() + cursorSize + magnifierAreaHeight))
        if magnifierArea.right() >= self.screenPixel.width():
            magnifierArea.moveLeft(self.mousePoint.x() - magnifierAreaWidth - cursorSize / 2)
        if magnifierArea.bottom() + fontAreaHeight >= self.screenPixel.height():
            magnifierArea.moveTop(self.mousePoint.y() - magnifierAreaHeight - cursorSize / 2 - fontAreaHeight)

        # third, draw the watch area to magnifier area
        watchAreaScaled = watchAreaPixmap.scaled(QSize(magnifierAreaWidth, magnifierAreaHeight))
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
        print(pointRgb)

        # draw information
        self.graphicsScene.addRect(QRectF(magnifierArea.bottomLeft(),
                                          magnifierArea.bottomRight() + QPoint(0, fontAreaHeight)),
                                   Qt.black,
                                   QBrush(Qt.black))
        rgbInfo = self.graphicsScene.addSimpleText(' Rgb: ({0}, {1}, {2})'.format(pointRgb.red(), pointRgb.green(), pointRgb.blue()))
        rgbInfo.setPos(magnifierArea.bottomLeft() + QPoint(0, 2))
        rgbInfo.setPen(QPen(QColor(255, 255, 255), 2))

        rect = self.selectedArea.normalized()
        sizeInfo = self.graphicsScene.addSimpleText(' Size: {0} x {1}'.format(rect.width(), rect.height()))
        sizeInfo.setPos(magnifierArea.bottomLeft() + QPoint(0, 2) + QPoint(0, fontAreaHeight / 2))
        sizeInfo.setPen(QPen(QColor(255, 255, 255), 2))

    def saveScreenshot(self):
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
        target = QRect(selected)
        target.moveTopLeft(QPoint(0, 0))

        image = QImage(source.size(), QImage.Format_RGB32)
        painter = QPainter(image)
        painter.begin(self)

        # remove the selected rect and drag points
        for junk in self.itemsToRemove:
            self.graphicsScene.removeItem(junk)

        self.graphicsScene.render(painter, QRectF(target), QRectF(source))
        painter.end()
        image.save('test', 'png', 10)

        # then add the selected rect and drag points background-color
        for junk in self.itemsToRemove:
            self.graphicsScene.addItem(junk)

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
            self.graphicsScene.addRect(0, 0, self.screenPixel.width(), self.screenPixel.height(), mask, mask)
        else:
            self.graphicsScene.addRect(0, 0, self.screenPixel.width(), topRightPoint.y(), mask, mask)
            self.graphicsScene.addRect(0, topLeftPoint.y(), topLeftPoint.x(), rect.height(), mask, mask)
            self.graphicsScene.addRect(topRightPoint.x() + 1, topRightPoint.y(),
                                       self.screenPixel.width() - topRightPoint.x(),
                                       rect.height(),
                                       mask,
                                       mask)
            self.graphicsScene.addRect(0, bottomLeftPoint.y() + 1,
                                       self.screenPixel.width(), self.screenPixel.height() - bottomLeftPoint.y(),
                                       mask, mask)

        # draw the magnifier
        if self.action == ACTION_SELECT:
            self.drawMagnifier()
            if self.mousePressed:
                self.drawSizeInfo()

        if self.action == ACTION_MOVE_SELECTED:
            self.drawSizeInfo()

        # draw the toolBar
        if self.action != ACTION_SELECT:
            spacing = 5
            dest = QPointF(rect.bottomRight() - QPointF(self.tooBar.width(), 0) - QPointF(spacing, -spacing))
            if dest.x() < spacing:
                dest.setX(spacing)
            if dest.y() + self.tooBar.height() >= self.screenPixel.height():
                if rect.top() - self.tooBar.height() < spacing:
                    dest.setY(rect.top() + spacing)
                else:
                    dest.setY(rect.top() - self.tooBar.height() - spacing)

            self.tooBar.move(dest.toPoint())
            self.penSetBar.move(dest.toPoint() + QPoint(0, self.tooBar.height() + spacing))
            print(self.tooBar.pos())
            self.tooBar.show()
            self.penSetBar.show()
        else:
            self.tooBar.hide()
            self.penSetBar.hide()

        # draw the list
        for step in self.drawListResult:
            self.drawOneStep(step)

        if self.drawListProcess is not None:
            self.drawOneStep(self.drawListProcess)

        if self.selectedArea != QRect():
            self.itemsToRemove = []

            # draw the selected rectangle
            pen = QPen(QColor(0, 255, 255), 2)
            self.itemsToRemove.append(self.graphicsScene.addRect(rect, pen))

            # draw the drag point
            radius = QPoint(3, 3)
            brush = QBrush(QColor(0, 255, 255))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(topLeftPoint - radius, topLeftPoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(topMiddlePoint - radius, topMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(topRightPoint - radius, topRightPoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(leftMiddlePoint - radius, leftMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(rightMiddlePoint - radius, rightMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(bottomLeftPoint - radius, bottomLeftPoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(bottomMiddlePoint - radius, bottomMiddlePoint + radius), pen, brush))
            self.itemsToRemove.append(self.graphicsScene.addEllipse(QRectF(bottomRightPoint - radius, bottomRightPoint + radius), pen, brush))

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

    # draw the size information on the top left corner
    def drawSizeInfo(self):
        sizeInfoAreaWidth = 100
        sizeInfoAreaHeight = 20
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

        self.graphicsScene.addRect(QRectF(sizeInfoArea), Qt.black, QBrush(Qt.black))

        sizeInfo = self.graphicsScene.addSimpleText('  {0} x {1}'.format(rect.width(), rect.height()))
        sizeInfo.setPos(sizeInfoArea.topLeft() + QPoint(0, 2))
        sizeInfo.setPen(QPen(QColor(255, 255, 255), 2))

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

    # slots
    def changeAction(self, nextAction):
        self.action = nextAction


if __name__ == "__main__":
    a = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    a.exec_()
