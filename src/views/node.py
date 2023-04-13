from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from utils.algs import *
from math import *


class Node(QGraphicsEllipseItem):
    def __init__(self, graphWidget):
        super().__init__()
        self.edgeSet = set()

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(0)
        self.initialBrush = None
        self.selectedEffect = {
            "adjustment": 2.5,
            "color": QColor(255, 100, 100)
        }
        self.selected = False

        self.newPos = QPointF(0, 0)
        self.graph = graphWidget

        self.id = -1
        self.label = None

        # self.bRect = QGraphicsRectItem(self)

    def setId(self, id):
        self.id = id
        self.prepareGeometryChange()

        if self.label is None:
            self.label = QGraphicsTextItem(self)

        self.label.setPlainText(str(self.id))
        self.label.setFont(self.graph.getGlobalFont())
        self.label.setDefaultTextColor(self.brush().color().darker(20))

        textRect = self.label.boundingRect()
        d = max(textRect.width(), textRect.height()) + 10

        self.setRect(-d/2, -d/2, d, d)

        self.label.setPos(self.boundingRect().center() -
                          self.label.boundingRect().center())

        for edge in self.edgeSet:
            edge.adjust()

        # self.bRect.setPen(QPen(Qt.green))
        # self.bRect.setBrush(Qt.transparent)
        # self.bRect.setRect(self.boundingRect())

    def getId(self):
        return self.id

    def setSelectedEffect(self, effect):
        self.selectedEffect = effect

    def addEdge(self, edge):
        self.edgeSet.add(edge)
        edge.adjust()

    def edges(self):
        return self.edgeSet

    def itemChange(self, change, value):
        # if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
        for edge in self.edgeSet:
            edge.adjust()
        return super().itemChange(change, value)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self) -> QRectF:
        return super().boundingRect().adjusted(-5, -5, 5, 5)

    def setSelected(self, selected):
        self.prepareGeometryChange()
        d = self.selectedEffect["adjustment"]
        c = self.selectedEffect["color"]
        self.selected = selected

        if selected:
            self.setRect(self.rect().adjusted(-d, -d, d, d))
            self.initialBrush = self.brush().color()
            self.setBrush(c)
            self.update()
        else:
            self.setRect(self.rect().adjusted(d, d, -d, -d))
            self.setBrush(self.initialBrush)
            self.update()
        return super().setSelected(selected)

    def isSelected(self):
        return self.selected
