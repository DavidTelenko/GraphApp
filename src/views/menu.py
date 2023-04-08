import functools
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MenuBar(QMenuBar):
    def __init__(self, layout, settings=None, parent=None):
        super(QMenuBar, self).__init__(parent)
        self.settings = settings or {}
        self.context = {}
        self._generateMenus(self, self.context, layout)

    def _getCallback(self, menuKey, tabKey, tabName):
        stringCallback = f'on_{menuKey}_{tabKey}'
        if (hasattr(self.parent(), stringCallback)):
            return getattr(self.parent(), stringCallback)

        stringCallback = f'on_{menuKey}_change'
        if (hasattr(self.parent(), stringCallback)):
            return functools.partial(
                getattr(self.parent(), stringCallback), (tabKey, tabName))

    def _generateTabs(self, menuBar, menuKey, context, layout):
        context["tabs"] = {}
        for tabKey, tabName in layout.items():
            shortcut = self.settings["shortcuts"].get(menuKey, {}).get(tabKey)
            shortcut = shortcut if shortcut is not None else ""
            callback = self._getCallback(menuKey, tabKey, tabName)

            if callback:
                tab = menuBar.addAction(tabName, callback, shortcut=shortcut)
            else:
                tab = menuBar.addAction(tabName)

            context["tabs"][tabKey] = tab

    def _generateMenus(self, menuBar, context, layout):
        context["menus"] = {}
        menus = context["menus"]

        for menuKey, menuData in layout.items():
            innerMenu = menuBar.addMenu(menuData["name"])
            menus[menuKey] = {"menu": innerMenu}

            if "menus" in menuData:
                self._generateMenus(
                    innerMenu,
                    menus[menuKey],
                    menuData["menus"],
                )

            if "tabs" in menuData:
                self._generateTabs(
                    innerMenu,
                    menuKey,
                    menus[menuKey],
                    menuData["tabs"],
                )
