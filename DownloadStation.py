from PyQt5.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QListView, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

import json
import requests
import sys
import time
import threading

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

        self.listTask.setModel(taskListModel)

        threading.Timer(2.0, self.loadTaskList).start()

    def registerDownload(self):
        # file = open('test.torrent', 'rb')
        # upload = {'file': file}
        # obj = {'data': "api=SYNO.DownloadStation2.Task&version=1&method=create&file=1234&type=file&create_list=true"}
        #
        # response = self.curSession.post(url="%s/webapi/DownloadStation/entry.cgi" %(synoURL),
        #                                 data=obj,
        #                                 files=upload).text
        # print(response)

        inputURLs = self.inputUrl.toPlainText()
        fileURL = inputURLs.split("\n")

        for URL in fileURL:
            response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi" %(self.synoURL),
                                            data="api=SYNO.DownloadStation.Task&version=1&method=create&uri=%s" %(URL)).text
            print(response)

        self.inputUrl.clear()
