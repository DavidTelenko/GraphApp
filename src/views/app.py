import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from views.menu import MenuBar
from views.viewport import GraphWidget
from views.inputProps import *
from utils import Resource
from pathlib import Path
import qdarktheme
from utils.algs import algs
from views.node import Node
from views.edge import Edge
import json


class Application(QMainWindow):
    def __init__(self, parent=None):
        super(Application, self).__init__(parent)

        self.resourcesPath = Path("resources")

        self.settings = Resource(self.resourcesPath / "settings.json")
        self.metadata = Resource(self.resourcesPath / "metadata.json")

        self.themes = {
            "dark": qdarktheme.load_stylesheet("dark"),
            "light": qdarktheme.load_stylesheet("light"),
            "default": "",
        }

        self.setWindowIcon(QIcon("resources/assets/icon.png"))
        self.setTheme()
        self.loadUI()
        self.currentFile = None

    def loadUI(self):
        menusLayoutPath = self.resourcesPath / "menus.json"

        self.menusLayout = Resource(menusLayoutPath)
        self.setMinimumSize(1000, 800)
        self.setMenuBar(MenuBar(self.menusLayout, self.settings, self))
        self.setCentralWidget(self.loadMain())
        self.setWindowTitle(self.metadata["appname"])

    def loadMain(self):
        self.graphWidget = GraphWidget(self)
        return self.graphWidget

    def setTheme(self):
        self.setStyleSheet(self.themes[self.settings["theme"]])

    def on_file_exit(self):
        self.destroy()
        sys.exit()

    def on_file_saveAs(self):
        filePath, _ = QFileDialog.getSaveFileName(
            filter=f"JSON File (*.json)",
            caption=""
        )
        if filePath:
            serialized = self.serializeGraph()
            with open(filePath, "w") as file:
                json.dump(serialized, file, indent=4)

    def on_file_open(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(f"JSON File (*.json)")
        if dialog.exec_():
            filePath = dialog.selectedFiles()[0]
            # try:
            with open(filePath, "r") as file:
                jsonFile = json.load(file)
                self.graphWidget = self.deserializeGraph(jsonFile)
                self.setCentralWidget(self.graphWidget)
            # except Exception as e:
            #     QMessageBox.critical(self, "Oh my God", str(e))

    def serializeGraph(self):
        json = {}

        json["structure"] = self.graphWidget.graph
        json["nodesVisuals"] = []

        for item in self.graphWidget.scene().items():
            if isinstance(item, Node):
                json["nodesVisuals"].append({
                    "pos": {
                        "x": item.pos().x(),
                        "y": item.pos().y(),
                    },
                    "id": item.getId()
                })
        return json

    def deserializeGraph(self, json):
        graphWidget = GraphWidget()

        graph = json["structure"]
        nodes = json["nodesVisuals"]

        nodeIndex = {}

        for node in nodes:
            nodeIndex[node["id"]] = graphWidget.addNode(
                QPointF(node["pos"]["x"],
                        node["pos"]["y"]), node["id"])

        for source, connected in graph.items():
            for dest, weight in connected.items():
                graphWidget.addEdge(nodeIndex[source], nodeIndex[dest], weight)

        return graphWidget

    def on_theme_change(self, themeData):
        themeKey, themeName = themeData
        self.settings["theme"] = themeKey
        self.setTheme()
        self.graphWidget.resizeEvent(QResizeEvent(
            self.graphWidget.size(), self.graphWidget.size()))

    def on_algorithms_change(self, algData):
        if algData[0] != "pushRelabel":
            return  # for now
        dialog = InputFlowProps(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        s, t = dialog.getInput()
        if s not in self.graphWidget.graph or t not in self.graphWidget.graph:
            QMessageBox.critical(
                self, "Error", "Source or target id is not in graph")
            return
        maxFlow = algs[algData[0]](self.graphWidget.graph, s, t)
        QMessageBox.information(
            self, "Result", f"Max flow of selected region is: {maxFlow}")

    def on_help_change(self, helpData):
        helpKey, helpName = helpData
        pagePath = self.resourcesPath / "pages" / f"{helpKey}.html"
        with open(pagePath, encoding="utf8") as file:
            QMessageBox.about(self, helpName, file.read())
