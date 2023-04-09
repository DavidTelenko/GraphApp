from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from views.menu import MenuBar
from views.viewport import GraphWidget
from utils import Resource
from pathlib import Path
import sys
import qdarktheme


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

    def loadUI(self):
        menusLayoutPath = self.resourcesPath / "strings" / \
            self.settings["locale"] / "menus.json"
        viewportStringPath = self.resourcesPath / "strings" / \
            self.settings["locale"] / "viewport.json"

        self.menusLayout = Resource(menusLayoutPath)
        self.viewportStrings = Resource(viewportStringPath)
        self.setMinimumSize(1000, 800)
        self.setMenuBar(MenuBar(self.menusLayout, self.settings, self))
        self.setCentralWidget(self.loadMain())
        self.setWindowTitle(self.metadata["appname"][self.settings["locale"]])

    def loadMain(self):
        return GraphWidget(self)
        # return QGraphicsView(Viewport(self, self.viewportStrings), self)

    def setTheme(self):
        self.setStyleSheet(self.themes[self.settings["theme"]])

    def on_file_exit(self):
        self.destroy()
        sys.exit()

    def on_lang_change(self, langData):
        langKey, langName = langData
        self.settings["locale"] = langKey
        self.loadUI()

    def on_theme_change(self, themeData):
        themeKey, themeName = themeData
        self.settings["theme"] = themeKey
        self.setTheme()

    def on_help_change(self, helpData):
        helpKey, helpName = helpData
        pagePath = self.resourcesPath / "pages" / \
            self.settings["locale"] / f"{helpKey}.html"
        with open(pagePath, encoding="utf8") as file:
            QMessageBox.about(self, helpName, file.read())

