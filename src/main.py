import webbrowser
import os
from datetime import datetime
from tkinter import *
from tkinter import ttk
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

    def make_window(self):
        self.master.title("레드마인 도우미")
        self.master.geometry("800x420+100+100")
        # self.master.geometry("400x140+100+100")
        self.master.resizable(True, True)

        self.mainFrame = Frame(self.master, relief="solid", bd=2)

        # scrollbar = Scrollbar(self.mainFrame, orient="vertical")
        # scrollbar.pack(side="right", fill="y")

        # 설정 초기화
        self.configuration()
        # 사용자 정보
        self.user_info()
        # 이슈번호
        #self.make_issue_comp()
        # 금일 한일
        #self.make_today_spendtime()

        # 지켜보고 있는 일감 소요시간 등록
        self.favorite_list_input_timeentries()

        self.errorMsg = StringVar()
        self.errorLabel = Label(self, textvariable=self.errorMsg, fg="red")
        self.errorLabel.grid(column=0, row=3, columnspan=3)

        self.mainFrame.pack()

    def configuration(self):
        if os.path.exists(user_json_path):
            with open(user_json_path, "r") as json_file:
                self.json_data = json.load(json_file)
            if self.json_data['apiKey']:
                apiKey = self.json_data['apiKey']
                self.redmine = Redmine(redmine_url, key=apiKey)
        else:
            self.json_data = None
            self.redmine = None


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
        if self.redmine:
            userName = self.json_data['userName']
            date = self.spendtimeDate.get()
            time_entries = self.redmine.time_entry.filter(user_id='me', spent_on=date)
            copyText = "[" + userName + "]\n"
            copyText += "* 레드마인 이슈\n"
            for time_entry in time_entries:
                issueId = time_entry.issue.id
                issue = self.redmine.issue.get(issueId)
                copyText += "\t. [] #" + str(issueId) + " " + issue.subject + "\n"

            pc.copy(copyText)
        else:
            alert.showinfo("알림", "API Key를 입력해주세요.")

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



    # 지켜보기 일감 소요시간 입력
    def favorite_list_input_timeentries(self):
        if self.redmine:
            issues = self.redmine.issue.filter(status_id='open', watcher_id='me')
            self.submitDatas = {}
            self.favoriteListCanvas = Canvas(self.mainFrame, width=750, height=340)
            self.favoriteListCanvas.grid(column=0, row=2, sticky="news")

            self.favoriteScroll = Scrollbar(self.mainFrame, orient="vertical", command=self.favoriteListCanvas.yview)
            self.favoriteScroll.grid(column=3, row=2, sticky='ns')
            self.favoriteListCanvas.configure(yscrollcommand=self.favoriteScroll.set)

            self.favoriteListFrame = Frame(self.favoriteListCanvas)
            self.favoriteListCanvas.create_window((0,0), window=self.favoriteListFrame, anchor="nw")

            self.favorite_list_header()
            for i in range(len(issues)):
                issue = issues[i]
                self.favorite_list_item(issue, i+1)

            self.favoriteButtons = Frame(self.master)
            self.favoriteButtons.pack(side=BOTTOM, pady=10)
            submitTimeEntries = Button(self.favoriteButtons, text="등록", command=self.submit_time_entries, width=30)
            submitTimeEntries.grid(column=0, row=0)
            reloadTimeEntries = Button(self.favoriteButtons, text="조회", command=self.reload_time_entries, width=30)
            reloadTimeEntries.grid(column=1, row=0, padx=10)

            self.favoriteListCanvas.config(scrollregion=self.favoriteListCanvas.bbox("all"))

    def favorite_list_header_label(self, text, col, width, labelWidth):
        label_frame = Frame(self.favoriteListFrame, width=width, bg="#dbdbdb", padx=10, pady=5)
        # label_frame.pack()
        label_frame.grid(column=col, row=0)
        if labelWidth:
            label = Label(label_frame, text=text, bg="#dbdbdb", width=labelWidth)
        else:
            label = Label(label_frame, text=text, bg="#dbdbdb")
        label.pack(fill=BOTH, expand=YES)

    def favorite_list_header(self):
        self.favorite_list_header_label("이슈번호", 0, 120, 10)
        self.favorite_list_header_label("제목", 1, 320, 40)
        self.favorite_list_header_label("작업일시", 2, 120, 10)
        self.favorite_list_header_label("작업종류", 3, 120, 20)
        self.favorite_list_header_label("소요시간", 4, 120, 10)

    def favorite_list_item_label(self, text, col, row, width, labelWidth, justify):
        label_frame = Frame(self.favoriteListFrame, width=width, padx=10, pady=5)
        label_frame.grid(column=col, row=row)
        anchor = None
        if justify == LEFT:
            anchor = "sw"

        if labelWidth:
            label = Label(label_frame, text=text, justify=justify, width=labelWidth, wraplength=labelWidth*7, anchor=anchor)
        else:
            label = Label(label_frame, text=text, justify=justify, anchor=anchor)
        label.pack()


    def favorite_list_item(self, issue, index):
        submitKey = str(issue.id) + "_" + str(index);
        self.favorite_list_item_label(issue.id, 0, index, 120, 10, CENTER)
        self.favorite_list_item_label(issue.subject, 1, index, 320, 40, LEFT)

        date = DateEntry(self.favoriteListFrame, values="Text", state="readonly", date_pattern="yyyy-mm-dd", width=10)
        date.grid(column=2, row=index)

        def favorite_list_item_date_change(event):
            self.submitDatas[submitKey]["spent_on"] = date.get()

        date.bind("<<DateEntrySelected>>", favorite_list_item_date_change)

        activities = issue.project.time_entry_activities
        optionNames = ["-- 선택 --"]
        optionValues = [-1]
        activityId = -1
        for activity in activities:
            optionNames.append(activity["name"])
            optionValues.append(activity["id"])
        n = StringVar()
        combobox = ttk.Combobox(self.favoriteListFrame, width=15, textvariable=n)
        combobox["values"] = optionNames

        combobox.grid(column=3, row=index)
        combobox.current()

        def favorite_list_item_combobox_change(event):
            index = event.widget.current()
            activityId = optionValues[index]
            self.submitDatas[submitKey]["activity_id"] = activityId

        combobox.bind("<<ComboboxSelected>>", favorite_list_item_combobox_change, optionValues)

        time = Entry(self.favoriteListFrame, width=10)
        time.grid(column=4, row=index)

        def favorite_list_item_time_input(event):
            self.submitDatas[submitKey]["hours"] = time.get()

        time.bind("<KeyRelease>", favorite_list_item_time_input)

        self.submitDatas[submitKey] = {
            "issue_id": issue.id,
            "spent_on": date.get(),
            "activity_id": activityId,
            "hours": None
        }

    def submit_time_entries(self):
        # valid = True
        # for key in self.submitDatas:
        #     activityId = self.submitDatas[key]["activity_id"]
        #     hours = self.submitDatas[key]["hours"]
        #     if activityId == -1 or not hours:
        #         valid = False
        #         break
        # if valid == False:
        #     alert.showinfo("알림", "작업종류와 소요시간을 입력하지 않으셨습니다.")
        # else:
        for key in self.submitDatas:
            issueId = self.submitDatas[key]["issue_id"]
            spendOn = self.submitDatas[key]["spent_on"]
            activityId = self.submitDatas[key]["activity_id"]
            hours = self.submitDatas[key]["hours"]
            if activityId >= 0 and hours:
                self.redmine.time_entry.create(
                    issue_id=issueId,
                    spend_on=spendOn,
                    hours=hours,
                    activity_id=activityId
                )
        self.reload_time_entries()


    def reload_time_entries(self):
        self.favoriteScroll.destroy()
        self.favoriteListFrame.destroy()
        self.favoriteListCanvas.destroy()
        self.favoriteButtons.destroy()
        self.favorite_list_input_timeentries()

if __name__ == '__main__':
    root = Tk()
    root.iconbitmap(Config.CONFIG_CONSTANTS["icon"])
    main_window = Main(master=root)
    root.mainloop()