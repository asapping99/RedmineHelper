# mypage.py
import webbrowser
from tkinter import *
from tkcalendar import DateEntry
import pyperclip as pc
import tkinter.messagebox as alert
import babel.numbers

class MyPage:

    def execute(self, root, redmine_url, json_data):
        self.root = root
        self.redmine_url = redmine_url
        self.json_data = json_data
        self.root.master.geometry("450x200+100+100")
        self.root.mainFrame.config(relief=None, bd=0)
        # 홈 이동 버튼
        self.home_button()
        # 이슈번호
        self.make_issue_comp()
        # 금일 한일
        self.make_today_spendtime()

    def home_button(self):
        homeBtn = Button(self.root.mainFrame, text="홈 으로...", command=self.move_home, width=30)
        homeBtn.grid(column=0, row=3, pady=50)

    def move_home(self):
        self.root.reload()

    def make_issue_comp(self):
        label = Label(self.root.mainFrame, text="이슈번호")
        label.grid(column=0, row=1, pady=10)
        # label.grid(column=0, row=0)

        reg = self.root.mainFrame.master.register(self.limit)
        self.issueNo = StringVar()
        self.textboxIssueNo = Entry(self.root.mainFrame, width=12, textvariable=self.issueNo, validate='key',
                                    validatecommand=(reg, '%P'))
        self.textboxIssueNo.grid(column=1, row=1, padx=5, pady=10)
        self.textboxIssueNo.focus()
        self.textboxIssueNo.bind("<Return>", self.on_enterkey)

        self.button = Button(self.root.mainFrame, text="열기", command=self.openClicked)
        self.button.grid(column=2, row=1, padx=5, pady=10)

    def make_today_spendtime(self):
        label2 = Label(self.root.mainFrame, text="일일 보고")
        label2.grid(column=0, row=2, pady=5)

        self.spendtimeDate = DateEntry(self.root.mainFrame, values="Text", state="readonly", date_pattern="yyyy-mm-dd")
        self.spendtimeDate.grid(column=1, row=2, padx=5, pady=5, sticky=W)

        self.button2 = Button(self.root.mainFrame, text="저장", command=self.saveTodaySpendTime)
        self.button2.grid(column=2, row=2, padx=5, pady=5)


    def openClicked(self):
        issueNo = self.textboxIssueNo.get()
        if issueNo is None or issueNo == "":
            alert.showinfo("알림", "이슈번호를 입력해 주세요.")
        else:
            webbrowser.open_new_tab(self.redmine_url+"/issues/"+issueNo)
            #webbrowser.open_new_tab(self.jsonData["server_url"] + "/issues/" + issueNo)


    def saveTodaySpendTime(self):
        # 클립보드에 저장
        if self.root.redmine:
            redmine = self.root.redmine
            userName = self.json_data['userName']
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