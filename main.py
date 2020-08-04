import json
import sys
import requests

from PyQt5.QtWidgets import QApplication, QListView, QPushButton, QTextEdit, QVBoxLayout, QWidget


class DownloadStation(QWidget):
    def __init__(self):
        super().__init__()

        with open('accounts.json', 'rt', encoding='UTF8') as json_file:
            global synoURL, synoID, synoPW

            jsonData = json.load(json_file)
            synoURL = jsonData["Server"]
            synoID = jsonData["ID"]
            synoPW = jsonData["PW"]

        self.curSession = requests.session()

        self.mainLayout = QVBoxLayout()

        self.btnDownload = QPushButton("Download")
        self.inputUrl = QTextEdit()
        self.listWorking = QListView()

        self.initUI(synoURL, synoID, synoPW)

    def initUI(self, synoURL, synoID, synoPW):
        self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" %(synoURL, synoID, synoPW))

        self.btnDownload.clicked.connect(self.registerDownload)
        self.inputUrl.setAcceptRichText(False)

        self.mainLayout.addWidget(self.listWorking)
        self.mainLayout.addWidget(self.inputUrl)
        self.mainLayout.addWidget(self.btnDownload)
        self.mainLayout.addStretch()

        self.setLayout(self.mainLayout)

        self.setWindowTitle("Download Station")
        self.move(300, 300)
        self.resize(400, 200)
        self.show()

    def registerDownload(self):
        inputURLs = self.inputUrl.toPlainText()
        fileURL = inputURLs.split("\n")

        for URL in fileURL:
            response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(synoURL),
                                            data="api=SYNO.DownloadStation.Task&version=1&method=create&uri=%s" %(URL)).text
            print(response)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute = DownloadStation()
    sys.exit(app.exec_())
