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


def calcWeightPos(sourcePoint: QPointF, destPoint: QPointF, textRect: QRectF, lineThickness: float):
    # calculate the midpoint of the line
    midPoint = sourcePoint + (destPoint - sourcePoint) / 2

    # calculate a vector orthogonal to the line
    perpendicular_vector = QLineF(
        sourcePoint, destPoint).normalVector().unitVector()

    # calculate a vector along the line
    line_vector = destPoint - sourcePoint
    line_length = QLineF(sourcePoint, destPoint).length()
    line_vector = QPointF(line_vector.x() / line_length,
                          line_vector.y() / line_length)

    # calculate the sign of the dot product between the text normal and the line vector
    text_normal = perpendicular_vector

    text_direction = QPointF(text_normal.dx(), text_normal.dy())
    line_direction = QPointF(line_vector.x(), line_vector.y())

    dot_product = QPointF.dotProduct(text_direction, line_direction)

    # offset the text position by half the text height plus the line thickness
    offset = (textRect.height() / 2) + lineThickness
    offset_vector = QPointF(perpendicular_vector.dx() * offset,
                            perpendicular_vector.dy() * offset)

    # calculate the position of the text item
    text_position = midPoint + offset_vector - \
        QPointF(textRect.width() / 2, textRect.height() / 2)

    return text_position


class Edge(QGraphicsItem):
    def __init__(self, sourceNode, destNode):
        super().__init__()
        self.source = sourceNode
        self.dest = destNode
        self.sourcePoint = QPointF()
        self.destPoint = QPointF()
        self.arrowSize = 10
        self.pen = QPen(Qt.black, 1, Qt.SolidLine,
                        Qt.RoundCap, Qt.RoundJoin)
        self.selectedEffect = QBrush(QColor(180, 80, 80))
        self.textColor = QColor(160, 160, 160)
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

    def setTextColor(self, effect):
        self.textColor = effect.color()

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

        self.textItem.setFont(self.source.graph.globalFont)
        self.textItem.setPlainText(str(self.weight))
        self.textItem.setDefaultTextColor(self.textColor)
        pos = calcWeightPos(self.source.pos(), self.dest.pos(),
                            self.textItem.boundingRect(), self.thickness)
        # pos = QPointF(pos.x() - self.textItem.boundingRect().width() / 2,
        #               pos.y() - self.textItem.boundingRect().height() / 2)
        self.textItem.setPos(pos)
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

    def shape(self):
        path = QPainterPath()
        path.moveTo(self.sourcePoint)
        if self.drawArrowHead:
            path.lineTo(self.destPoint)
            path.addPolygon(QPolygonF(self.arrowHead))
        else:
            path.lineTo(self.destPoint)

        stroker = QPainterPathStroker()
        stroker.setWidth(max(self.pen.width(), 20))
        return stroker.createStroke(path)

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
