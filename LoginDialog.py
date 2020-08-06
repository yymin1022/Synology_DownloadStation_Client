from PyQt5.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QWidget

import requests

import main


class LoginDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.mainLayout = QVBoxLayout()

        self.btnLogin = QPushButton("Login")
        self.inputID = QTextEdit()
        self.inputPW = QTextEdit()

        self.initUI()

    def initUI(self):
        self.inputID.setAcceptRichText(False)
        self.inputPW.setAcceptRichText(False)

        self.mainLayout.addWidget(self.inputID)
        self.mainLayout.addWidget(self.inputPW)
        self.mainLayout.addWidget(self.btnLogin)
        self.mainLayout.addStretch()

        self.mainUI.setLayout(self.mainLayout)

        self.mainUI.setWindowTitle("Download Station")
        self.mainUI.move(300, 300)
        self.mainUI.resize(400, 200)
        self.mainUI.show()
