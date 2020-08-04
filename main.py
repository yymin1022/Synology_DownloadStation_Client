import json
import requests
import sys

from PyQt5.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QListView, QPushButton, QTextEdit, QVBoxLayout, QWidget


class DownloadStation(QWidget):
    def __init__(self):
        super().__init__()

        self.curSession = requests.session()

        self.mainLayout = QVBoxLayout()

        self.btnDownload = QPushButton("Download")
        self.inputUrl = QTextEdit()
        self.listTask = QListView()

        self.initUI()
        self.initSession()

    def initUI(self):
        self.btnDownload.clicked.connect(self.registerDownload)
        self.inputUrl.setAcceptRichText(False)

        self.mainLayout.addWidget(self.listTask)
        self.mainLayout.addWidget(self.inputUrl)
        self.mainLayout.addWidget(self.btnDownload)
        self.mainLayout.addStretch()

        self.setLayout(self.mainLayout)

        self.setWindowTitle("Download Station")
        self.move(300, 300)
        self.resize(400, 200)
        self.show()

    def initSession(self):
        with open('accounts.json', 'rt', encoding='UTF8') as json_file:
            global synoURL, synoID, synoPW

            jsonData = json.load(json_file)
            synoURL = jsonData["Server"]
            synoID = jsonData["ID"]
            synoPW = jsonData["PW"]

        self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" %(synoURL, synoID, synoPW))
        self.loadTaskList()

    def loadTaskList(self):
        responseJSON = self.curSession.get("http://defcon.or.kr:85/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list&additional=transfer").text

        # print(responseJSON)

        taskJSON = json.loads(responseJSON)
        taskList = taskJSON["data"]["tasks"]

        taskListModel = QStandardItemModel()

        for task in taskList:
            status = task["status"]
            item = QStandardItem("%s / %s" % (task["title"], status))

            if status == "downloading":
                percentage = (task["additional"]["transfer"]["size_downloaded"] / task["size"]) * 100
                item = QStandardItem("%s / %s / %d%% / %1.fMB/S" %(task["title"], status, percentage, task["additional"]["transfer"]["speed_download"] / 1000000))

                item.setForeground(QBrush(QColor(0, 0, 0)))
            elif status == "finished":
                item.setForeground(QBrush(QColor(0, 0, 255)))
            elif status == "waiting":
                item.setForeground(QBrush(QColor(255, 128, 0)))
            elif status == "error":
                item.setForeground(QBrush(QColor(255, 0, 0)))
            elif status == "paused":
                item.setForeground(QBrush(QColor(128, 128, 128)))

            taskListModel.appendRow(item)

        self.listTask.setModel(taskListModel)

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
