from PyQt5.QtWidgets import QApplication

import json
import sys

import AESCipher
import DownloadStation
import LoginDialog


class main():
    def __init__(self):
        self.initLogin()

    def initLogin(self):
        try:
            with open('accounts.uum', 'rt', encoding='UTF8') as json_file:
                self.loadData = AESCipher.AESCipher().decrypt_str(json_file.readline())

                self.encryptData = json.loads(self.loadData)
                self.synoURL = self.encryptData["Server"]
                self.synoID = self.encryptData["ID"]
                self.synoPW = self.encryptData["PW"]

            self.openDownloadStation(self.synoURL, self.synoID, self.synoPW, self.isOTP)
        except FileNotFoundError:
            self.openLogin()

    def openDownloadStation(self, synoURL, synoID, synoPW, isOTP):
        self.window = DownloadStation.DownloadStation(synoURL, synoID, synoPW, isOTP)

    def openLogin(self):
        self.window = LoginDialog.LoginDialog()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute = main()
    sys.exit(app.exec_())
