import webbrowser
import os
from tkinter import *
import tkinter.messagebox as alert
import config.config as Config
import pyperclip as pc
from redminelib import Redmine
import json
from tkcalendar import DateEntry
from babel.numbers import *

user_json_path = "./user_info.json"
redmine_url = Config.CONFIG_CONSTANTS["server_url"]

class Main(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.pack_propagate(0)
        self.pack()
        self.execute(self)

    @staticmethod
    def execute(self):
        #with open("config.json", "r") as f:
        #    self.jsonData = json.load(f)
        self.make_window()

    def reload(self):
        self.destroy()
        self.__init__()

    def openClicked(self):
        issueNo = self.textboxIssueNo.get()
        if issueNo is None or issueNo == "":
            self.errorMsg.set("이슈번호를 입력해 주세요.")
        else:
            self.errorMsg.set("")
            self.issueNo.set("")
            webbrowser.open_new_tab(redmine_url+"/issues/"+issueNo)
            #webbrowser.open_new_tab(self.jsonData["server_url"] + "/issues/" + issueNo)

    def saveTodaySpendTime(self):
        # 클립보드에 저장
        if self.json_data and self.json_data['apiKey']:
            apiKey = self.json_data['apiKey']
            userName = self.json_data['userName']
            redmine = Redmine(redmine_url, key=apiKey)
            date = self.spendtimeDate.get()
            time_entries = redmine.time_entry.filter(user_id='me', spent_on=date)
            copyText = "[" + userName + "]\n"
            copyText += "* 레드마인 이슈\n"
            for time_entry in time_entries:
                issueId = time_entry.issue.id
                issue = redmine.issue.get(issueId)
                copyText += "\t. [] #" + str(issueId) + " " + issue.subject + "\n"

            pc.copy(copyText)
        else:
            alert.showinfo("알림", "API Key를 입력해주세요.")

    def make_window(self):
        self.master.title("레드마인 도우미")
        self.master.geometry("400x140+100+100")
        self.master.resizable(False, False)
        # 설정 초기화
        self.configuration()
        # 사용자 정보
        self.user_info()
        # 이슈번호
        self.make_issue_comp()
        # 금일 한일
        self.make_today_spendtime()

        self.errorMsg = StringVar()
        self.errorLabel = Label(self, textvariable=self.errorMsg, fg="red")
        self.errorLabel.grid(column=0, row=3, columnspan=3)

    def configuration(self):
        if os.path.exists(user_json_path):
            with open(user_json_path, "r") as json_file:
                self.json_data = json.load(json_file)
        else:
            self.json_data = None

    def saveUserInfo(self):
        userName = self.textboxUserName.get()
        apiKey = self.textboxApiKey.get()
        if userName is None or userName == "":
            alert.showinfo("알림", "사용자 이름을 입력해 주세요.")
        elif apiKey is None or apiKey == "":
            alert.showinfo("알림", "API Key를 입력해 주세요.")
        else:
            data = {
                "userName": userName,
                "apiKey": apiKey
            }
            with open(user_json_path, 'w') as outfile:
                json.dump(data, outfile)

            self.reload()


    def user_info(self):

        if not self.json_data or (not self.json_data['userName'] and not self.json_data['apiKey']):
            label = Label(self, text="사용자 명")
            label.grid(column=0, row=0, pady=5)

            self.userName = StringVar()
            self.textboxUserName = Entry(self, width=12, textvariable=self.userName)
            self.textboxUserName.grid(column=1, row=0, padx=5, pady=5)

            label = Label(self, text="API Key")
            label.grid(column=2, row=0, pady=5)

            self.apiKey = StringVar()
            self.textboxApiKey = Entry(self, width=12, textvariable=self.apiKey)
            self.textboxApiKey.grid(column=3, row=0, padx=10, pady=5)

            self.button = Button(self, text="저장", command=self.saveUserInfo)
            self.button.grid(column=4, row=0, padx=5, pady=10)


    def make_issue_comp(self):
        label = Label(self, text="이슈번호")
        label.grid(column=0, row=1, pady=10)
        # label.grid(column=0, row=0)

        reg = root.register(self.limit)
        self.issueNo = StringVar()
        self.textboxIssueNo = Entry(self, width=12, textvariable=self.issueNo, validate='key',
                                    validatecommand=(reg, '%P'))
        self.textboxIssueNo.grid(column=1, row=1, padx=5, pady=10)
        self.textboxIssueNo.focus()
        self.textboxIssueNo.bind("<Return>", self.on_enterkey)

        self.button = Button(self, text="열기", command=self.openClicked)
        self.button.grid(column=2, row=1, padx=5, pady=10)


    def make_today_spendtime(self):
        label2 = Label(self, text="일일 보고")
        label2.grid(column=0, row=2, pady=5)

        self.spendtimeDate = DateEntry(self, values="Text", state="readonly", date_pattern="yyyy-mm-dd")
        self.spendtimeDate.grid(column=1, row=2, padx=5, pady=5, sticky=W)

        self.button2 = Button(self, text="저장", command=self.saveTodaySpendTime)
        self.button2.grid(column=2, row=2, padx=5, pady=5)


    def limit(self, text):
        MAX_DIGITS = 12
        try:
            int(text)
        except ValueError:
            valid = (text == '')  # Invalid unless it's just empty.
        else:
            valid = (len(text) <= MAX_DIGITS)   # OK unless it's too long.
        if not valid:
            print("유효하지 않음")

        return valid

    def on_enterkey(self, event):
        self.button.invoke()




if __name__ == '__main__':
    root = Tk()
    root.iconbitmap(Config.CONFIG_CONSTANTS["project_dir"] + Config.CONFIG_CONSTANTS["icon"])
    main_window = Main(master=root)
    root.mainloop()