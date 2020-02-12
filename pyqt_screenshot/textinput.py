from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton


class TextInput(QWidget):
    # used when input text

    inputChanged = pyqtSignal()
    okPressed = pyqtSignal()
    cancelPressed = pyqtSignal()

    def __init__(self, parent=None):
        super(TextInput, self).__init__(parent)

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        self.mainLayout = QVBoxLayout()
        self.textArea = QTextEdit(self)

        self.buttonArea = QWidget(self)
        self.buttonLayout = QHBoxLayout()
        self.cancelButton = QPushButton('Cancel', self)
        self.okButton = QPushButton('Ok', self)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.okButton)
        self.buttonArea.setLayout(self.buttonLayout)

        self.mainLayout.addWidget(self.textArea)
        self.mainLayout.addWidget(self.buttonArea)
        self.setLayout(self.mainLayout)

        self.textArea.textChanged.connect(self.textChanged_)
        self.okButton.clicked.connect(self.okButtonClicked)
        self.cancelButton.clicked.connect(self.cancelPressed)

    def getText(self):
        return self.textArea.toPlainText()

    def getFocus(self):
        self.setFocus()
        self.textArea.setFocus()

    def clearText(self):
        self.textArea.clear()

    # slots
    def textChanged_(self):
        self.inputChanged.emit()

    def cancelButtonClicked(self):
        self.cancelPressed.emit()

    def okButtonClicked(self):
        self.okPressed.emit()
