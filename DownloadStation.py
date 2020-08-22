from PyQt5.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView, QMenu, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

import json
import requests

import main


class DownloadStation(QWidget):
    def __init__(self, url, id, pw):
        super().__init__()

        self.synoURL = url
        self.synoID = id
        self.synoPW = pw

        self.curSession = requests.session()

        self.mainLayout = QVBoxLayout()

        self.btnDownload = QPushButton("Download")
        self.btnReload = QPushButton("Reload")
        self.inputUrl = QTextEdit()
        self.listTask = QListView()

        self.initUI()
        self.initSession()

    def initUI(self):
        self.btnDownload.clicked.connect(self.registerDownload)
        self.btnReload.clicked.connect(self.loadTaskList)
        self.inputUrl.setAcceptRichText(False)
        self.listTask.clicked.connect(self.manageTask)

        self.mainLayout.addWidget(self.btnReload)
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
        sessionData = self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" %(self.synoURL, self.synoID, self.synoPW))
        isSessionSuccess = json.loads(sessionData.text)["success"]

        if isSessionSuccess:
            self.loadTaskList()
        else:
            reinitializeAccount = QMessageBox.question(self, "Login Error", "Need to Login again.", QMessageBox.Yes)
            if reinitializeAccount == QMessageBox.Yes:
                main.main.openLogin(main)
                self.close()

    def loadTaskList(self):
        self.taskIDList = []

        responseJSON = self.curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list&additional=transfer" %(self.synoURL)).text

        taskJSON = json.loads(responseJSON)
        taskList = taskJSON["data"]["tasks"]

        taskListModel = QStandardItemModel()

        for task in taskList:
            status = task["status"]
            item = QStandardItem("%s / %s" %(task["title"], status))
            item.setEditable(False)

            if status == "downloading":
                percentage = 0
                if task["size"] != 0:
                    percentage = (task["additional"]["transfer"]["size_downloaded"] / task["size"]) * 100
                item = QStandardItem("%s / %s / %d%% / %1.fMB/S" %(task["title"], status, percentage, task["additional"]["transfer"]["speed_download"] / 1000000))
                item.setEditable(False)
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
            self.taskIDList.append(task["id"])

        self.listTask.setModel(taskListModel)

    def manageTask(self, modelIndex):
        curIndex = modelIndex.row()

        menu = QMenu(self)
        copy_action = menu.addAction("복사하기")
        quit_action = menu.addAction("Quit")
        action = menu.exec_()
        if action == quit_action:
            pass
        elif action == copy_action:
            print("copy...")

        print(self.taskIDList[curIndex])

    def registerDownload(self):
        file = open('test.torrent', 'rb')

        args = {
            'api': 'SYNO.DownloadStation.Task',
            'version': '1',
            'method': 'create',
            'session': 'DownloadStation'
        }
        files = {'file': ('test.torrent', file)}

        response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(self.synoURL),
                                        data=args,
                                        files=files).text
        print(response)

        # with open('test.torrent', 'rb') as payload:
        #     args = {
        #         'api': 'SYNO.DownloadStation.Task',
        #         'version': '1',
        #         'method': 'create',
        #         'session': 'DownloadStation'
        #     }
        #     files = {'file': ('test.torrent', payload)}
        #     r = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(self.synoURL), data=args, files=files, verify=False)
        #     print(r.text)

        # inputURLs = self.inputUrl.toPlainText()
        # fileURL = inputURLs.split("\n")
        #
        # for URL in fileURL:
        #     response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(self.synoURL),
        #                                     data="api=SYNO.DownloadStation.Task&version=1&method=create&uri=%s" %(URL)).text
        #     print(response)
        #
        # self.inputUrl.clear()
