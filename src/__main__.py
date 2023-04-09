from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from views.app import Application


def main():
    import sys

    app = QApplication(sys.argv)

    Application().show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
