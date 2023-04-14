from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pprint import pprint
from utils.algs import *
from math import *
from views.node import Node
from views.edge import Edge


class GraphWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)

        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.dragPos = None

        self.globalFont = QFont("Arial", 8)

        self.id = 0
        self.graph = {}
        self.selectedNodes = []
        self.selectedEdges = []
        self.nodePressed = False

        self.lastMousePress = None

        self.minMaxWeight = (1, 1)

        self.sourceNode = None

        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(scene)

        self.selectionRect = QGraphicsRectItem()
        self.selectionRect.setBrush(QColor(190, 0, 150, 50))
        self.selectionRect.setPen(QPen(QColor(190, 0, 150), 0.5))
        self.scene().addItem(self.selectionRect)

        self.scale(3.0, 3.0)

    def getGlobalFont(self):
        return self.globalFont

    def setGlobalFont(self, font):
        self.globalFont = font

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # print(selectedNodes)
        # print(selectedEdges)

        if event.key() == Qt.Key_F2:

            if len(self.selectedNodes) == 1 and len(self.selectedEdges) == 0:
                text, okPressed = QInputDialog.getText(
                    self,
                    QCoreApplication.translate(str(self.__class__),
                                               "New id:"),
                    QCoreApplication.translate(str(self.__class__),
                                               "Please enter the new id:"))
                if okPressed:
                    self.renameNode(self.selectedNodes[0], text)
                    self.clearSelection()
                return

            if len(self.selectedEdges) == 1 and len(self.selectedNodes) == 0:
                weight, okPressed = QInputDialog.getInt(
                    self,
                    QCoreApplication.translate(str(self.__class__),
                                               "New weight:"),
                    QCoreApplication.translate(str(self.__class__),
                                               "Please enter the new weight:"))
                if okPressed:
                    self.renameEdge(self.selectedEdges[0], weight)
                    self.clearSelection()
                return

        if event.key() == Qt.Key_N:
            if len(self.selectedNodes) != 2:
                return
            source, dest = self.selectedNodes
            self.addEdge(source, dest, 1)
            self.clearSelection()

        if event.key() == Qt.Key_Delete:
            for item in self.selectedNodes:
                self.removeNode(item)
            for item in self.selectedEdges:
                self.removeEdge(item)
            self.selectedNodes.clear()
            self.selectedEdges.clear()

        return super().keyPressEvent(event)

    def addNode(self, pos, text=None):
        newNode = Node(self)
        newNode.setRect(-10, -10, 20, 20)
        newNode.setPen(QPen(Qt.NoPen))
        newNode.setBrush(QColor(150, 150, 150))
        newNode.setTextColor(QColor(60, 60, 60))
        newNode.setPos(pos)
        while str(self.id) in self.graph:
            self.id += 1
        id = str(self.id) if text is None else text
        newNode.setId(id)
        self.graph[id] = {}

        self.scene().addItem(newNode)
        # pprint(self.graph)
        return newNode

    def addEdge(self, src, dest, weight=1):
        if dest.getId() in self.graph[src.getId()]:
            return

        self.graph[src.getId()][dest.getId()] = weight

        if src.getId() in self.graph[dest.getId()]:
            for edge in dest.edgeSet:
                if edge.source == dest and edge.dest == src:
                    src.addEdge(edge)
                    edge.drawArrowHead = False
                    edge.adjust()
                    return

        edge = Edge(src, dest)

        edge.setWeight(weight)
        edge.setPen(QPen(QColor(100, 100, 100)))
        edge.setBrush(QBrush(QColor(100, 100, 100)))
        edge.setTextColor(QBrush(QColor(40, 140, 220)))

        src.addEdge(edge)

        self.scene().addItem(edge)
        self.adjustAllEdges()
        return edge

    def renameNode(self, node, newId):
        if renameNode(self.graph, node.getId(), newId):
            node.setId(newId)
        else:
            QMessageBox.critical(
                self, "Error", f"Id {newId} is already in the graph")
        # pprint(self.graph)

    def renameEdge(self, edge, newWeight):
        if newWeight == 0:
            QMessageBox.critical(
                self, "Error", f"Weight cannot be zero")
            return

        reweightEdge(self.graph, edge.sourceNode().getId(),
                     edge.destNode().getId(), newWeight)
        edge.setWeight(newWeight)
        # pprint(self.graph)

    def removeNode(self, node):
        self.scene().removeItem(node)

        for edge in node.edges():
            self.scene().removeItem(edge)
        deleteNode(self.graph, node.getId())

        # pprint(self.graph)

    def removeEdge(self, edge):
        self.scene().removeItem(edge)

        dest = edge.dest
        src = edge.source

        dest.edgeSet.discard(src.getId())
        src.edgeSet.discard(dest.getId())

        deleteEdge(self.graph, edge.sourceNode().getId(),
                   edge.destNode().getId())
        # pprint(self.graph)

    def getFirstNode(self, items):
        if items is not None:
            for item in items:
                if isinstance(item, Node):
                    return item

    def getFirstEdge(self, items):
        if items is not None:
            for item in items:
                if isinstance(item, Edge):
                    return item

    def adjustAllEdges(self):
        for item in self.scene().items():
            if isinstance(item, Edge):
                item.adjust()

    def addNodeIfPossible(self, pos, items):
        if not items and not self.selectedEdges and not self.selectedNodes:
            self.addNode(pos)

    def dragScreenStart(self, pos, items):
        if (self.verticalScrollBar().isVisible() or
                self.horizontalScrollBar().isVisible() and not self.nodePressed):
            self.setCursor(Qt.ClosedHandCursor)
            self.dragPos = pos
            return

        self.dragPos = None

    def dragScreenBody(self, pos):
        if self.dragPos is None or self.nodePressed:
            return

        delta = self.dragPos - pos
        self.dragPos = pos

        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() + delta.y())

        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() + delta.x())

    def dragScreenEnd(self):
        if self.dragPos is not None or self.nodePressed:
            self.setCursor(Qt.ArrowCursor)
        self.dragPos = None

    def selectionRoutineStart(self, pos):
        if self.nodePressed:
            return
        self.lastMousePress = pos
        self.selectionRect.setRect(
            QRectF(self.lastMousePress, self.lastMousePress))

    def selectionRoutineBody(self, pos):
        if self.nodePressed:
            return
        self.selectionRect.setRect(QRectF(self.lastMousePress, pos))

    def selectionRoutineEnd(self, select=True):
        if self.nodePressed or self.lastMousePress is None:
            return
        selected = self.scene().items(self.selectionRect.rect())
        self.selectionRect.setRect(
            QRectF(self.lastMousePress, self.lastMousePress))
        if select:
            self.selectItems(selected)

    def clearSelection(self):
        for item in self.selectedNodes + self.selectedEdges:
            item.setSelected(False)
        self.selectedNodes.clear()
        self.selectedEdges.clear()

    def selectOrDeselect(self, item, selected):
        if item.isSelected():
            item.setSelected(False)
            selected.remove(item)
        else:
            item.setSelected(True)
            selected.append(item)

    def selectItems(self, selected):
        if not len(selected):
            self.clearSelection()
            return
        for item in selected:
            if isinstance(item, Node):
                self.selectOrDeselect(item, self.selectedNodes)
            elif isinstance(item, Edge):
                self.selectOrDeselect(item, self.selectedEdges)

    def checkNodePressed(self, items):
        self.nodePressed = False
        for item in items:
            if isinstance(item, Node):
                self.nodePressed = True
                return item

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(
            QRectF(0, 0, 1, 1)).width()
        if factor < 1 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)

        pos = self.mapToScene(event.pos())
        items = self.scene().items(pos)
        # self.checkNodePressed(items)
        self.nodePressed = len(items) != 0

        if event.button() == Qt.LeftButton and event.modifiers() == Qt.ControlModifier:
            self.selectItems(items)

        elif event.button() == Qt.LeftButton:
            self.selectionRoutineStart(pos)

        elif event.button() == Qt.RightButton:
            self.dragScreenStart(event.pos(), items)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)

        pos = self.mapToScene(event.pos())

        if event.buttons() == Qt.LeftButton and event.modifiers() == Qt.NoModifier:
            self.selectionRoutineBody(pos)

        elif event.buttons() == Qt.RightButton:
            self.dragScreenBody(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

        pos = self.mapToScene(event.pos())
        items = self.scene().items(pos)

        if event.button() == Qt.LeftButton:
            self.addNodeIfPossible(pos, items)
            self.selectionRoutineEnd(event.modifiers() == Qt.NoModifier)

        elif event.button() == Qt.RightButton:
            self.dragScreenEnd()
        # print(self.selected)

    def wheelEvent(self, event):
        self.scaleView(pow(2, event.angleDelta().y() / 240.0))

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        size = event.size()
        scene = self.scene()
        scene.setSceneRect(0, 0,
                           max(scene.width(), size.width()),
                           max(scene.height(), size.height()))
