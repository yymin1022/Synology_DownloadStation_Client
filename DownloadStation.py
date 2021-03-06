from PyQt5.QtGui import QBrush, QColor, QCursor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QInputDialog, QListView, QMenu, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

import json
import requests

import main


class DownloadStation(QWidget):
    def __init__(self, url, id, pw, otp):
        super().__init__()

        self.synoURL = url
        self.synoID = id
        self.synoPW = pw
        self.isOTP = otp

        self.curSession = requests.session()

        self.mainLayout = QVBoxLayout()

        self.btnDownload = QPushButton("다운로드")
        self.btnReload = QPushButton("새로고침")
        self.inputUrl = QTextEdit()
        self.listTask = QListView()

        self.initUI()
        self.initSession()

    def initUI(self):
        self.btnDownload.clicked.connect(self.registerDownload)
        self.btnReload.clicked.connect(self.loadTaskList)
        self.inputUrl.setAcceptRichText(False)
        self.inputUrl.setPlaceholderText("ex) https://test.synology.me/a93hfGF\nex) movie.torrent")
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
        try:
            if self.isOTP == "True":
                self.otpCode = ""
                while True:
                    codeInput, btnOK = QInputDialog.getText(self, 'OTP 인증', 'OTP 코드를 입력하세요.')

                    if btnOK:
                        self.otpCode = str(codeInput)
                    else:
                        # Pushed Cancel Button : Re-show Dialog
                        continue
                    sessionData = self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStation&format=cookie&otp_code=%s"
                                                      %(self.synoURL, self.synoID, self.synoPW, self.otpCode))
                    self.isSessionSuccess = json.loads(sessionData.text)["success"]

                    if self.isSessionSuccess:
                        self.loadTaskList()
                    else:
                        reinitializeAccount = QMessageBox.question(self, "OTP 오류",
                                                                   "OTP 코드가 올바르지 않습니다.",
                                                                   QMessageBox.Yes, QMessageBox.No)
                        if reinitializeAccount == QMessageBox.Yes:
                            # Re-input Code
                            continue
                        elif reinitializeAccount == QMessageBox.No:
                            # Finish
                            self.close()
                    break
            else:
                sessionData = self.curSession.get("%s/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStation&format=cookie"
                                                  %(self.synoURL, self.synoID, self.synoPW))
                self.isSessionSuccess = json.loads(sessionData.text)["success"]

                if self.isSessionSuccess:
                    self.loadTaskList()
                else:
                    reinitializeAccount = QMessageBox.question(self, "로그인 불가", "권한이 없거나 존재하지 않는 계정입니다.\n다시 로그인 해주세요.",
                                                               QMessageBox.Yes)
                    if reinitializeAccount == QMessageBox.Yes:
                        main.main.openLogin(main)
                        self.close()
        except:
            reinitializeAccount = QMessageBox.question(self, "서버 오류", "서버 주소가 올바르지 않거나 접속할 수 없습니다.", QMessageBox.Yes)
            if reinitializeAccount == QMessageBox.Yes:
                main.main.openLogin(main)
                self.close()


    def loadTaskList(self):
        self.taskIDList = []

        responseJSON = self.curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list&additional=transfer"
                                           %(self.synoURL)).text

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

        if len(self.taskIDList) == 0:
            item = QStandardItem("진행중인 작업이 없습니다.")
            item.setEditable(False)
            item.setForeground(QBrush(QColor(128, 128, 128)))
            taskListModel.appendRow(item)

        self.listTask.setModel(taskListModel)

    def manageTask(self, modelIndex):
        if modelIndex.data() != "진행중인 작업이 없습니다.":
            curIndex = modelIndex.row()

            menu = QMenu(self)
            actionPause = menu.addAction("일시정지")
            actionResume = menu.addAction("이어받기")
            actionCancel = menu.addAction("삭제")

            curAction = menu.exec_(QCursor.pos())
            if curAction == actionPause:
                response = self.curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=pause&id=%s"
                                               %(self.synoURL, self.taskIDList[curIndex]))
            elif curAction == actionResume:
                response = self.curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=resume&id=%s"
                                               %(self.synoURL, self.taskIDList[curIndex]))
            elif curAction == actionCancel:
                cancelFile = QMessageBox.question(self, "작업 삭제", "선택한 작업을 취소하고 다운로드중이던 파일을 삭제합니다.", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if cancelFile == QMessageBox.Yes:
                    response = self.curSession.get("%s/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=delete&id=%s&force_complete=false"
                                                   %(self.synoURL, self.taskIDList[curIndex]))

            self.loadTaskList()

    def registerDownload(self):
        inputURLs = self.inputUrl.toPlainText()
        fileURL = inputURLs.split("\n")

        for URL in fileURL:
            if URL.endswith(".torrent"):
                try:
                    file = open(URL, 'rb')

                    args = {
                        'api': 'SYNO.DownloadStation.Task',
                        'version': '1',
                        'method': 'create',
                        'session': 'DownloadStation'
                    }
                    files = {'file': (URL, file)}

                    response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi"
                                                        %(self.synoURL),
                                                    data=args,
                                                    files=files)
                except FileNotFoundError:
                    QMessageBox.question(self, "파일 오류", "%s를 찾을 수 없습니다." %(URL), QMessageBox.Yes)
            else:
                response = self.curSession.post(url="%s/webapi/DownloadStation/task.cgi"
                                                    %(self.synoURL),
                                                data="api=SYNO.DownloadStation.Task&version=1&method=create&uri=%s"
                                                     %(URL))
            self.loadTaskList()

        self.inputUrl.clear()
