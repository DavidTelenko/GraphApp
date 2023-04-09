from random import randint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pprint import pprint
from utils.algs import deleteNode, renameNode, remap
from math import *


def calcArrow(startPoint, endPoint, w, radius=0):
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


class GraphWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timerId = 0
        self.centerNode = None
        scene = QGraphicsScene(self)

        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)

        self.setScene(scene)

        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        node1 = Node(self)
        node2 = Node(self)

        node1.setRect(-10, -10, 20, 20)
        node1.setPen(QPen(Qt.NoPen))
        node1.setBrush(Qt.red)

        node2.setRect(-10, -10, 20, 20)
        node2.setPen(QPen(Qt.NoPen))
        node2.setBrush(Qt.red)

        self.scene().addItem(node1)
        self.scene().addItem(node2)

        pprint(self.scene().items())

        edge1 = Edge(node1, node2)

        self.scene().addItem(edge1)

        node1.setPos(50, 50)
        node2.setPos(0, 100)

        pprint(self.scene().items())

        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))

    def itemMoved(self):
        if (not self.timerId):
            self.timerId = self.startTimer(1000 // 25)

    def mousePressEvent(self, event):
        """Add a new node when the user clicks on an empty space."""
        pos = self.mapToScene(event.pos())
        items = self.scene().items(pos)

        if items:
            return

        newNode = Node(self)
        newNode.setRect(-10, -10, 20, 20)
        newNode.setPen(QPen(Qt.NoPen))
        newNode.setBrush(Qt.red)
        newNode.setPos(pos)
        self.scene().addItem(newNode)

    # @pyqtSlot()
    # def zoomIn(self):
    #     pass

    # @pyqtSlot()
    # def zoomOut(self):
    #     self.scaleView(1 / 1.2)

    def timerEvent(self, event):
        nodes = []
        items = self.scene().items()

        for item in items:
            if isinstance(item, Node):
                nodes.append(item)

        for node in nodes:
            node.calculateForces()

        itemsMoved = False
        for node in nodes:
            if node.advancePosition():
                itemsMoved = True

        if not itemsMoved:
            self.killTimer(self.timerId)
            self.timerId = 0

    def wheelEvent(self, event):
        self.scaleView(pow(2, event.angleDelta().y() / 240.0))

    def drawBackground(self, painter, rect):
        pass

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(
            QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)


class Node(QGraphicsEllipseItem):
    def __init__(self, graphWidget: GraphWidget):
        super().__init__()

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        self.setZValue(-1)

        self.edgeList = []
        self.newPos = QPointF(0, 0)
        self.graph = graphWidget

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def calculateForces(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self.newPos = self.pos()
            return

        # Sum up all forces pushing this item away
        xvel = 0.0
        yvel = 0.0
        for node in self.scene().items():
            if (node is None):
                continue
            vec = self.mapToItem(node, 0, 0)
            dx = vec.x()
            dy = vec.y()
            l = 2.0 * (dx * dx + dy * dy)
            if (l > 0):
                xvel += (dx * 150.0) / l
                yvel += (dy * 150.0) / l

        # Now subtract all forces pulling items together
        weight = (len(self.edgeList) + 1) * 10
        for edge in self.edgeList:
            if edge.sourceNode() == self:
                vec = self.mapToItem(edge.destNode(), 0, 0)
            else:
                vec = self.mapToItem(edge.sourceNode(), 0, 0)
            xvel -= vec.x() / weight
            yvel -= vec.y() / weight

        if (qAbs(xvel) < 0.1 and qAbs(yvel) < 0.1):
            xvel = yvel = 0

        sceneRect = self.scene().sceneRect()
        self.newPos = self.pos() + QPointF(xvel, yvel)
        self.newPos.setX(
            min(max(self.newPos.x(), sceneRect.left() + 10), sceneRect.right() - 10))
        self.newPos.setY(
            min(max(self.newPos.y(), sceneRect.top() + 10), sceneRect.bottom() - 10))

    def advancePosition(self):
        if (self.newPos == self.pos()):
            return False

        self.setPos(self.newPos)
        return True

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edgeList:
                edge.adjust()
            self.graph.itemMoved()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super().mouseReleaseEvent(event)


class Edge(QGraphicsItem):
    def __init__(self, sourceNode, destNode):
        super().__init__()
        self.source = sourceNode
        self.dest = destNode
        self.sourcePoint = QPointF()
        self.destPoint = QPointF()
        self.arrowSize = 10

        self.setAcceptedMouseButtons(Qt.NoButton)
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.adjust()

    def sourceNode(self):
        return self.source

    def destNode(self):
        return self.dest

    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QLineF(self.mapFromItem(self.source, 0, 0),
                      self.mapFromItem(self.dest, 0, 0))
        length = line.length()

        self.prepareGeometryChange()

        if length < 20:
            self.sourcePoint = self.destPoint = line.p1()
            return

        edgeOffset = QPointF((line.dx() * 10) / length,
                             (line.dy() * 10) / length)
        self.sourcePoint = line.p1() + edgeOffset
        self.destPoint = line.p2() - edgeOffset

    def paint(self, painter, option, widget):
        if (not self.source or not self.dest):
            return

        line = QLineF(self.sourcePoint, self.destPoint)

        if (qFuzzyCompare(line.length(), 0)):
            return

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine,
                       Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(line)
        angle = atan2(-line.dy(), line.dx())

        sourceArrowP1 = self.sourcePoint + QPointF(sin(angle + pi / 3) * self.arrowSize,
                                                   cos(angle + pi / 3) * self.arrowSize)
        sourceArrowP2 = self.sourcePoint + QPointF(sin(angle + pi - pi / 3) * self.arrowSize,
                                                   cos(angle + pi - pi / 3) * self.arrowSize)

        destArrowP1 = self.destPoint + QPointF(sin(angle - pi / 3) * self.arrowSize,
                                               cos(angle - pi / 3) * self.arrowSize)
        destArrowP2 = self.destPoint + QPointF(sin(angle - pi + pi / 3) * self.arrowSize,
                                               cos(angle - pi + pi / 3) * self.arrowSize)

        painter.setBrush(Qt.black)
        painter.drawPolygon(
            QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        painter.drawPolygon(QPolygonF([line.p2(), destArrowP1, destArrowP2]))

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
                endPoint, arrowHead = calcArrow(p1, p2, w, d2 / 2)

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
                self.startHintPos, self.currentPos, w)
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
