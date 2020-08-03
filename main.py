import json
import requests


def main():
    with open('accounts.json', 'rt', encoding='UTF8') as json_file:
        json_data = json.load(json_file)
        id = json_data["id"]
        pw = json_data["pw"]

    curSession = requests.session()

    response = curSession.get("http://defcon.or.kr:85/webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=%s&passwd=%s&session=DownloadStationn&format=cookie" %(id, pw)).text
    print(response)

    response = curSession.get("http://defcon.or.kr:85/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list").text
    print(response)


if __name__ == '__main__':
    main()
