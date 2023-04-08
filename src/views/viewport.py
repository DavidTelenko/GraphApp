from random import randint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pprint import pprint
from utils.algs import deleteNode, renameNode, remap
from math import *


def calcArrow(qp, startPoint, endPoint, w, radius=0):
    arrowHeight, arrowWidth = w * 2 + w, w * 1.5

    dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

    length = sqrt(dx ** 2 + dy ** 2)

    normX, normY = dx / length, dy / length
    perpX, perpY = -normY, normX

    offsetRadiusX, offsetRadiusY = normX * radius, normY * radius

    leftX = endPoint.x() + arrowHeight * normX + arrowWidth * perpX + offsetRadiusX
    leftY = endPoint.y() + arrowHeight * normY + arrowWidth * perpY + offsetRadiusY

    rightX = endPoint.x() + arrowHeight * normX - arrowWidth * perpX + offsetRadiusX
    rightY = endPoint.y() + arrowHeight * normY - arrowWidth * perpY + offsetRadiusY

    arrowEndPoint = QPointF(endPoint.x() + offsetRadiusX,
                            endPoint.y() + offsetRadiusY)

    point2 = QPointF(leftX, leftY)
    point3 = QPointF(rightX, rightY)

    newEndPoint = QPointF(endPoint.x() + offsetRadiusX + arrowHeight * normX,
                          endPoint.y() + offsetRadiusY + arrowHeight * normY)

    return newEndPoint, [point2, arrowEndPoint, point3]


class Viewport(QGraphicsScene):
    def __init__(self, parent, strings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.strings = strings
        self.id = 0
        self.graph = {}
        self.points = {}
        self.currentPos = QPoint(0, 0)

        self.startHintPos = None
        self.arcDest = None
        self.aboutToDelete = False
        self.minMaxWeight = (1, 1)
        self.edgeHint = None

        self.graphicsItems = []

        self.icons = {}
        self.icons["rubbish"] = QPixmap("resources/assets/rubbish-bin.png")
        self.icons["rubbish-opened"] = QPixmap(
            "resources/assets/rubbish-bin-opened.png")

        self.scaleIcons()
        self.calculateRemoveArea()

        self.pressed = self.moving = False
        self.selected = None

    # def wheelEvent(self, event: QWheelEvent):

    def mousePressEvent(self, event):
        self.currentPos = event.scenePos()

        if event.button() == Qt.LeftButton:
            selected = self.select(self.currentPos)
            if selected is not None:
                self.selected = selected
                return

        elif event.button() == Qt.RightButton:
            selected = self.select(self.currentPos)
            if selected is not None:
                self.selected = selected
                self.startHintPos = self.currentPos
                return

        self.update()

    def mouseMoveEvent(self, event):
        self.currentPos = event.scenePos()
        print(self.currentPos)

        if event.buttons() & Qt.LeftButton:
            if self.selected is not None:
                self.points[self.selected] = (
                    event.scenePos(), self.points[self.selected][1])
                self.aboutToDelete = self.removeArea.contains(
                    self.currentPos)

        elif event.buttons() & Qt.RightButton:
            if self.startHintPos is not None:
                selected = self.select(self.currentPos)
                self.arcDest = selected

        self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.removeArea.contains(self.currentPos) and self.selected is None:
                self.graph = {}
                self.points = {}
                self.id = 0
                self.selected = None

            selected = self.select(event.scenePos())

            if selected is not None:
                text, okPressed = QInputDialog.getText(
                    self, "Text Input Dialog", self.strings["idPromt"])
                if okPressed:
                    self.points[text] = self.points[selected]
                    del self.points[selected]
                    renameNode(self.graph, selected, text)
                    self.repaint()
                    self.repaint()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.removeArea.contains(self.currentPos) and self.selected is None:
                pass

            elif self.selected is None:
                self.points[self.id] = (self.currentPos, None)
                self.graph[self.id] = {}
                self.id += 1

            elif self.aboutToDelete:
                del self.points[self.selected]
                deleteNode(self.graph, self.selected)
                self.aboutToDelete = False

            self.selected = None

        elif event.button() == Qt.RightButton:
            if self.selected is not None and self.arcDest is not None:
                weight = randint(1, 100)

                self.graph.setdefault(self.selected, {})[
                    self.arcDest] = weight

                self.minMaxWeight = min(self.minMaxWeight[0], weight), max(
                    self.minMaxWeight[1], weight)

            self.selected = None
            self.startHintPos = None
            self.arcDest = None

        pprint(self.graph)

        self.update()

    def resizeEvent(self, e: QResizeEvent):
        self.calculateRemoveArea()

    def drawForeground(self, qp: QPainter, rect):
        font = QFont("Arial", 12)

        qp.setRenderHint(QPainter.Antialiasing)

        # draw edges
        for (origin, dest) in self.graph.items():
            for (nodeId, weight) in dest.items():
                p1, d1 = self.points[origin]
                p2, d2 = self.points[nodeId]

                if nodeId == origin:
                    qp.setBrush(Qt.transparent)
                    qp.drawEllipse(p1-QPointF(d1/2, d1/2), d1/2, d1/2)
                    continue

                w = remap(
                    weight, self.minMaxWeight[0], self.minMaxWeight[1] + 1, 3, 10)
                endPoint, arrowHead = calcArrow(qp, p1, p2, w, d2 / 2)

                qp.setPen(QPen(QColor(150, 150, 150), w))
                qp.drawLine(p1, endPoint)

                qp.setPen(QPen(QColor(150, 150, 150), 2))
                qp.setBrush(QColor(150, 150, 150))
                qp.drawPolygon(QPolygonF(arrowHead))

        qp.setBrush(QColor(100, 100, 100))
        qp.setFont(font)

        # draw arrow hint
        w = 5
        qp.setPen(QPen(QColor(100, 100, 100), w))
        if self.startHintPos is not None:
            endPoint, arrowHead = calcArrow(
                qp, self.startHintPos, self.currentPos, w)
            qp.setPen(QPen(QColor(100, 100, 100), w))
            qp.drawLine(self.startHintPos, endPoint)

            qp.setPen(QPen(QColor(100, 100, 100), 2))
            qp.setBrush(QColor(100, 100, 100))
            qp.drawPolygon(QPolygonF(arrowHead))

        # draw nodes
        for (id, (p, _)) in self.points.items():
            text = str(id)
            textRect = qp.boundingRect(self.sceneRect(), Qt.AlignCenter, text)
            textRect.moveCenter(p)

            d = max(textRect.width(), textRect.height()) + 30
            ellipseRect = QRectF(0, 0, d, d)
            ellipseRect.moveCenter(p)

            self.points[id] = p, d

            if id == self.selected or id == self.arcDest:
                ellipseRect.adjust(-5, -5, 5, 5)
                qp.setBrush(QColor(255, 100, 100))

            qp.setPen(QPen(Qt.transparent, 0))
            qp.drawEllipse(ellipseRect)
            qp.setBrush(QColor(100, 100, 100))

            qp.setPen(QPen(Qt.white, 5))
            textRect.translate(ellipseRect.center() - textRect.center())
            qp.drawText(QRectF(textRect), text)

        # draw edge hint
        if self.edgeHint is not None:
            pos, text = self.edgeHint
            textRect = qp.boundingRect(self.sceneRect(), Qt.AlignCenter, text)
            textRect.moveBottomRight(pos)

            qp.setPen(QPen(Qt.transparent, 0))
            qp.setBrush(QColor(0, 0, 0, 50))
            qp.drawRect(textRect)

            qp.setPen(QPen(Qt.white, 5))
            qp.drawText(QRectF(textRect), text)

        # draw rubbish bin
        # icon = self.icons["rubbish-opened"] if self.aboutToDelete else self.icons["rubbish"]
        # qp.drawPixmap(self.removeArea, icon)

    def scaleIcons(self):
        self.icons["rubbish"] = self.icons["rubbish"].scaled(
            self.icons["rubbish"].width() // 8,
            self.icons["rubbish"].height() // 8,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.icons["rubbish-opened"] = self.icons["rubbish-opened"].scaled(
            self.icons["rubbish-opened"].width() // 8,
            self.icons["rubbish-opened"].height() // 8,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

    def calculateRemoveArea(self):
        iconData: QPixmap = self.icons["rubbish"]
        self.removeArea = iconData.rect()
        self.removeArea = QRectF(self.removeArea.x(),
                                 self.removeArea.y(),
                                 self.removeArea.width(),
                                 self.removeArea.height())
        self.removeArea.moveTopLeft(self.sceneRect().bottomRight() -
                                    iconData.rect().bottomRight() - QPoint(10, 10))

    def select(self, point):
        for id, (p, d) in self.points.items():
            if (point - p).manhattanLength() < d:
                return id
