from PyQt5.QtWidgets import QApplication

import json
import sys

import DownloadStation
import LoginDialog


class main():
    def __init__(self):
        with open('accounts.json', 'rt', encoding='UTF8') as json_file:
            global synoURL, synoID, synoPW

            jsonData = json.load(json_file)
            synoURL = jsonData["Server"]
            synoID = jsonData["ID"]
            synoPW = jsonData["PW"]

        DownloadStation.DownloadStation(synoURL, synoID, synoPW)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute = main()
    sys.exit(app.exec_())
