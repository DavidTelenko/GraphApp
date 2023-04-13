from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from utils.algs import *
from math import *


def calcArrow(sourcePoint, destPoint, w, radius=0):
    arrowHeight, arrowWidth = w * 2 + w, w * 1.5

    dx, dy = sourcePoint.x() - destPoint.x(), sourcePoint.y() - destPoint.y()

    length = sqrt(dx ** 2 + dy ** 2)

    normX, normY = dx / length, dy / length
    perpX, perpY = -normY, normX

    offsetRadiusX, offsetRadiusY = normX * radius, normY * radius

    leftX = destPoint.x() + arrowHeight * normX + \
        arrowWidth * perpX + offsetRadiusX
    leftY = destPoint.y() + arrowHeight * normY + \
        arrowWidth * perpY + offsetRadiusY

    rightX = destPoint.x() + arrowHeight * normX - \
        arrowWidth * perpX + offsetRadiusX
    rightY = destPoint.y() + arrowHeight * normY - \
        arrowWidth * perpY + offsetRadiusY

    arrowEndPoint = QPointF(destPoint.x() + offsetRadiusX,
                            destPoint.y() + offsetRadiusY)

    point2 = QPointF(leftX, leftY)
    point3 = QPointF(rightX, rightY)

    newEndPoint = QPointF(destPoint.x() + offsetRadiusX + arrowHeight * normX,
                          destPoint.y() + offsetRadiusY + arrowHeight * normY)

    return newEndPoint, [point2, arrowEndPoint, point3]


def calcWeightPos(sourcePoint, destPoint):
    dx, dy = sourcePoint.x() - destPoint.x(), sourcePoint.y() - destPoint.y()

    length = sqrt(dx ** 2 + dy ** 2)
    normX, normY = dx / length, dy / length
    # perpX, perpY = -normY, normX

    return QPointF(sourcePoint.x() - normX * (length / 2),
                   sourcePoint.y() - normY * (length / 2))


class Edge(QGraphicsItem):
    def __init__(self, sourceNode, destNode):
        super().__init__()
        # self.bRect = QGraphicsRectItem(self)
        self.source = sourceNode
        self.dest = destNode
        self.sourcePoint = QPointF()
        self.destPoint = QPointF()
        self.arrowSize = 10
        self.pen = QPen(Qt.black, 1, Qt.SolidLine,
                        Qt.RoundCap, Qt.RoundJoin)
        self.selectedEffect = QBrush(QColor(180, 80, 80))
        self.initialBrush = None
        self.selected = False
        self.brush = QBrush(Qt.black)
        self.setZValue(-1)

        self.weight = 1
        self.textItem = QGraphicsTextItem(self)
        self.thickness = 1
        self.drawArrowHead = True

        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source.addEdge(self)
        self.dest.addEdge(self)

        self.adjust()

    def setSelectedEffect(self, effect):
        self.selectedEffect = effect

    def sourceNode(self):
        return self.source

    def destNode(self):
        return self.dest

    def setWeight(self, weight):
        self.weight = weight
        self.adjust()

    def setSelected(self, selected):
        # print(f"Edge selected: {selected}")
        self.selected = selected
        if selected:
            self.pen.setColor(self.selectedEffect.color())
            self.brush = self.selectedEffect
        else:
            self.pen.setColor(self.initialBrush.color())
            self.brush = self.initialBrush
        self.update()
        return super().setSelected(selected)

    def adjust(self):
        if self.source == self.dest:
            # self.loop = QGraphicsEllipseItem(self)
            # self.loop.setPen(self.pen)
            # self.loop.setRect(self.dest.rect())
            # self.loop.setBrush(Qt.transparent)
            # destRect = self.dest.rect()
            # self.loop.rect().moveCenter(QPointF(100, 100))
            return

        minW, maxW = self.dest.graph.minMaxWeight
        minW, maxW = min(minW, self.weight), max(maxW, self.weight)
        self.dest.graph.minMaxWeight = minW, maxW

        self.thickness = remap(self.weight, minW, maxW + 1, 3, 7)

        self.sourcePoint = self.source.pos()
        self.destPoint = self.dest.pos()
        # draw text str(weight)

        if self.drawArrowHead:
            self.destPoint, self.arrowHead = calcArrow(
                self.sourcePoint,
                self.dest.pos(), self.thickness,
                self.dest.rect().width() / 2)

        pos = calcWeightPos(self.source.pos(), self.dest.pos())
        self.textItem.setFont(self.source.graph.globalFont)
        self.textItem.setPlainText(str(self.weight))
        self.textItem.setDefaultTextColor(self.brush.color().darker(20))
        # pos = QPointF(pos.x() - self.textItem.boundingRect().width() / 2,
        #               pos.y() - self.textItem.boundingRect().height() / 2)
        self.textItem.setPos(pos)

        # self.bRect.setPen(QPen(Qt.green))
        # self.bRect.setBrush(Qt.transparent)
        # self.bRect.setRect(self.boundingRect())
        self.update()

    def setPen(self, pen):
        self.pen = pen

    def setBrush(self, brush):
        self.brush = brush
        self.initialBrush = self.brush

    def paint(self, painter, option, widget):
        if (not self.source or not self.dest):
            return

        if (self.source == self.dest):
            # painter.drawEllipse(self.loop.rect())
            return

        line = QLineF(self.sourcePoint, self.destPoint)

        if (qFuzzyCompare(line.length(), 0)):
            return

        self.pen.setWidth(int(self.thickness))
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawLine(line)
        painter.setPen(Qt.NoPen)

        if self.drawArrowHead:
            painter.drawPolygon(QPolygonF(self.arrowHead))

    def boundingRect(self):
        if not self.source or not self.dest:
            return QRectF()

        penWidth = 1
        extra = (penWidth + self.arrowSize) / 2.0

        return QRectF(
            self.sourcePoint, QSizeF(
                self.destPoint.x() - self.sourcePoint.x(),
                self.destPoint.y() - self.sourcePoint.y())
        ).normalized().adjusted(-extra, -extra, extra, extra)
