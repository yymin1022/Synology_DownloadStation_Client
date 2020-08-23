from PyQt5.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

import AESCipher
import main


class LoginDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.loginLayout = QVBoxLayout()

        self.btnLogin = QPushButton("Login")
        self.inputID = QTextEdit()
        self.inputPW = QTextEdit()
        self.inputURL = QTextEdit()
        self.labelID = QLabel("DSM Account ID")
        self.labelPW = QLabel("DSM Account PW")
        self.labelURL = QLabel("DSM URL")

        self.initUI()

    def initUI(self):
        self.btnLogin.clicked.connect(self.saveAccount)
        self.inputID.setAcceptRichText(False)
        self.inputPW.setAcceptRichText(False)
        self.inputURL.setAcceptRichText(False)
        self.inputURL.setPlaceholderText("http://hello.synology.me")

        self.loginLayout.addWidget(self.labelURL)
        self.loginLayout.addWidget(self.inputURL)
        self.loginLayout.addWidget(self.labelID)
        self.loginLayout.addWidget(self.inputID)
        self.loginLayout.addWidget(self.labelPW)
        self.loginLayout.addWidget(self.inputPW)
        self.loginLayout.addWidget(self.btnLogin)
        self.loginLayout.addStretch()

        self.setLayout(self.loginLayout)

        self.setWindowTitle("Login Required")
        self.move(300, 300)
        self.resize(400, 200)
        self.show()

    def saveAccount(self):
        self.synoURL = self.inputURL.toPlainText()
        self.synoID = self.inputID.toPlainText()
        self.synoPW = self.inputPW.toPlainText()

        with open('accounts.uum', 'w', encoding='UTF8') as json_file:
            fileData = "{\n\"Server\":\"%s\",\n\"ID\": \"%s\",\n\"PW\": \"%s\"\n}" %(self.synoURL, self.synoID, self.synoPW)
            encryptData = AESCipher.AESCipher().encrypt_str(fileData)
            json_file.write(encryptData)

        main.main.openDownloadStation(main.main, self.synoURL, self.synoID, self.synoPW)
        self.close()
