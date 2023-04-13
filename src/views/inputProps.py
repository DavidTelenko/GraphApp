
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class InputFlowProps(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.s_label = QLabel(
            QCoreApplication.translate(str(self.__class__),
                                       "Enter 's' id:"))
        self.s_input = QLineEdit()
        self.t_label = QLabel(
            QCoreApplication.translate(str(self.__class__),
                                       "Enter 't' id:"))
        self.t_input = QLineEdit()

        mainLayout = QVBoxLayout()

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # create grid layout and add widgets to it
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.s_label, 0, 0)
        gridLayout.addWidget(self.s_input, 0, 1)
        gridLayout.addWidget(self.t_label, 1, 0)
        gridLayout.addWidget(self.t_input, 1, 1)

        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle(
            QCoreApplication.translate(str(self.__class__),
                                       "Please enter source and target."))

    def getInput(self):
        # returns tuple of s and t inputs
        return self.s_input.text(), self.t_input.text()
