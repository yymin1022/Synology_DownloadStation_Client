import json
import sys
import requests

from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget

class DownloadStation(QWidget):

    def __init__(self):
        super().__init__()

        with open('accounts.json', 'rt', encoding='UTF8') as json_file:
            global synoURL, synoID, synoPW

            jsonData = json.load(json_file)
            synoURL = jsonData["Server"]
            synoID = jsonData["ID"]
            synoPW = jsonData["PW"]

        self.initUI(synoURL, synoID, synoPW)

    def initUI(self, synoURL, synoID, synoPW):
        self.curSession = requests.session()
        self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" % (synoURL, synoID, synoPW))

        self.btnDownload = QPushButton("Download")
        self.inputUrl = QTextEdit()

        self.inputUrl.setAcceptRichText(False)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.inputUrl)
        mainLayout.addWidget(self.btnDownload)
        mainLayout.addStretch()

        self.setLayout(mainLayout)

        self.setWindowTitle("Download Station")
        self.move(300, 300)
        self.resize(400, 200)
        self.show()


# def main():
#     with open('accounts.json', 'rt', encoding='UTF8') as json_file:
#         jsonData = json.load(json_file)
#         synoURL = jsonData["Server"]
#         synoID = jsonData["ID"]
#         synoPW = jsonData["PW"]
#
#     curSession = requests.session()
#
#     response = curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" %(synoURL, synoID, synoPW)).text
#     print(response)
#
#     response = curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(synoURL), data="api=SYNO.DownloadStation.Task&version=1&method=create&uri=http://defcon.or.kr:85/sharing/qC2bgQIOt").text
#     print(response)
#
#     response = curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list&additional=detail,file" %(synoURL)).text
#     print(response)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute = DownloadStation()
    sys.exit(app.exec_())
