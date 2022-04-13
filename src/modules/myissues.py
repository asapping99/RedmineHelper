# myissues.py
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter.font import *
from tkinter import ttk
from tkcalendar import DateEntry
import pyperclip as pc

class MyIssues:
    # 내가 맡은 일감
    def execute(self, root):
        self.root = root
        self.root.master.geometry("1120x420+100+100")
        self.root.mainFrame.config(relief="solid", bd=2)
        self.myissues_list()

    def myissues_list(self):
        if self.root.redmine:
            user = self.root.redmine.user.get("current")
            issues = self.root.redmine.issue.filter(status_id="open", assigned_to_id=user.id,
                                                    sort="priority:desc,updated_on:desc", group_by="project")
            self.submitDatas = {}
            # 스크롤바를 위한 캔버스
            self.myissuesListCanvas = Canvas(self.root.mainFrame, width=1070, height=340)
            self.myissuesListCanvas.grid(column=0, row=2, sticky="news")
            # 스크롤바
            self.myissuesScroll = Scrollbar(self.root.mainFrame, orient="vertical", command=self.myissuesListCanvas.yview)
            self.myissuesScroll.grid(column=3, row=2, sticky='ns')
            self.myissuesListCanvas.configure(yscrollcommand=self.myissuesScroll.set)
            # 리스트 프레임
            self.myissuesListFrame = Frame(self.myissuesListCanvas)
            self.myissuesListCanvas.create_window((0,0), window=self.myissuesListFrame, anchor="nw")
            # 마우스 휠
            def scrollMouseWheel(event):
                self.myissuesListCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

            self.myissuesListCanvas.bind_all("<MouseWheel>", scrollMouseWheel)
            # 목록 헤더
            self.myissues_list_header()
            # 목록 데이터
            cntList = 1
            currentProjectId = -1
            for i in range(len(issues)):
                issue = issues[i]
                if currentProjectId != issue.project.id:
                    self.myissues_list_project_item(issue.project, cntList)
                    cntList += 1
                    currentProjectId = issue.project.id
                self.myissues_list_item(issue, cntList)
                cntList += 1

            # 하단 버튼들
            self.myissuesButtons = Frame(self.root.master)
            self.myissuesButtons.pack(side=BOTTOM, pady=10)
            ## 등록버튼
            submitTimeEntries = Button(self.myissuesButtons, text="등록", command=self.submit_time_entries, width=30)
            submitTimeEntries.grid(column=0, row=0, padx=30)
            ## 조회버튼

            reloadTimeEntries = Button(self.myissuesButtons, text="조회", command=self.reload_time_entries, width=30)
            reloadTimeEntries.grid(column=2, row=0)
            ## 홈으로 이동
            homeBtn = Button(self.myissuesButtons, text="홈 으로...", command=self.move_home, width=30)
            homeBtn.grid(column=3, row=0, padx=50)

            self.myissuesListCanvas.config(scrollregion=self.myissuesListCanvas.bbox("all"))


    def move_home(self):
        self.myissuesScroll.destroy()
        self.myissuesListFrame.destroy()
        self.myissuesListCanvas.destroy()
        self.myissuesButtons.destroy()
        self.root.reload()

    def myissues_list_header_label(self, text, col, width, labelWidth):
        label_frame = Frame(self.myissuesListFrame, width=width, bg="#dbdbdb", padx=10, pady=5)
        # label_frame.pack()
        label_frame.grid(column=col, row=0)
        if labelWidth:
            label = Label(label_frame, text=text, bg="#dbdbdb", width=labelWidth)
        else:
            label = Label(label_frame, text=text, bg="#dbdbdb")
        label.pack(fill=BOTH, expand=YES)

    def myissues_list_header(self):
        self.myissues_list_header_label("이슈번호", 0, 120, 10)
        self.myissues_list_header_label("제목", 1, 320, 40)
        self.myissues_list_header_label("작업일시", 2, 120, 10)
        self.myissues_list_header_label("작업종류", 3, 120, 20)
        self.myissues_list_header_label("소요시간", 4, 120, 10)
        self.myissues_list_header_label("설명", 5, 250, 42)


    def myissues_list_item_label(self, text, col, row, width, labelWidth, justify, cursor="arrow"):
        label_frame = Frame(self.myissuesListFrame, width=width, padx=10, pady=5)
        label_frame.grid(column=col, row=row)
        anchor = None
        if justify == LEFT:
            anchor = "sw"

        if labelWidth:
            label = Label(label_frame, text=text, justify=justify, width=labelWidth, wraplength=labelWidth*7, anchor=anchor, cursor=cursor)
        else:
            label = Label(label_frame, text=text, justify=justify, anchor=anchor, cursor=cursor)
        label.pack()
        return label


    def myissues_list_item(self, issue, index):
        submitKey = str(issue.id) + "_" + str(index);
        # 이슈번호
        def move_issue_page(event):
            webbrowser.open_new_tab(self.root.redmine_url + "/issues/" + str(issue.id))

        issueLabel = self.myissues_list_item_label(issue.id, 0, index, 120, 10, CENTER)
        issueLabel.config(highlightcolor="#dbdbdb", font=Font(underline=True, size=9), fg="#3F48CC")
        issueLabel.bind("<Button-1>", move_issue_page)
        # 제목
        def clipboard_subject(event):
            pc.copy(issue.subject)

        subjectLabel = self.myissues_list_item_label(issue.subject, 1, index, 320, 40, LEFT)
        subjectLabel.config(highlightcolor="#dbdbdb", font=Font(size=9), fg="#3F48CC")
        subjectLabel.bind("<Button-1>", clipboard_subject)
        # 작업일시
        date = DateEntry(self.myissuesListFrame, values="Text", state="readonly", date_pattern="yyyy-mm-dd", width=10)
        date.grid(column=2, row=index)

        def myissues_list_item_date_change(event):
            self.submitDatas[submitKey]["spent_on"] = date.get()

        date.bind("<<DateEntrySelected>>", myissues_list_item_date_change)

        # 작업종류
        activities = issue.project.time_entry_activities
        optionNames = ["-- 선택 --"]
        optionValues = [-1]
        activityId = -1
        for activity in activities:
            optionNames.append(activity["name"])
            optionValues.append(activity["id"])
        n = StringVar()
        combobox = ttk.Combobox(self.myissuesListFrame, width=15, textvariable=n, state="readonly")
        combobox["values"] = optionNames

        combobox.grid(column=3, row=index)
        combobox.current()
        def init_combobox():
            combobox.current(0)

        self.root.after(0, init_combobox)

        def myissues_list_item_combobox_change(event):
            index = event.widget.current()
            activityId = optionValues[index]
            self.submitDatas[submitKey]["activity_id"] = activityId

        combobox.bind("<<ComboboxSelected>>", myissues_list_item_combobox_change, optionValues)

        # 소요시간
        timeSV = StringVar()
        def myissues_list_item_time_input(*args):
            self.submitDatas[submitKey]["hours"] = timeSV.get()

        timeSV.trace("w", myissues_list_item_time_input)
        time = Entry(self.myissuesListFrame, width=10, textvariable=timeSV)
        time.grid(column=4, row=index)

        # 설명
        commentsSV = StringVar()
        def myissues_list_item_comments_input(*args):
            self.submitDatas[submitKey]["comments"] = commentsSV.get()

        commentsSV.trace("w", myissues_list_item_comments_input)
        comments = Entry(self.myissuesListFrame, width=40, textvariable=commentsSV)
        comments.grid(column=5, row=index)

        # 등록 데이터 초기화
        self.submitDatas[submitKey] = {
            "issue_id": issue.id,
            "spent_on": date.get(),
            "activity_id": activityId,
            "hours": None,
            "comments": None
        }

    def myissues_list_project_item(self, project, index):
        # 제목
        projectName = f"[ {project.name} ]"
        wraplength = 45 * 7
        label_frame = Frame(self.myissuesListFrame, width=400, padx=10, pady=5)
        label_frame.grid(column=0, row=index, columnspan=2)
        projectLabel = Label(label_frame, text=projectName, justify=LEFT, width=45,
              wraplength=wraplength, anchor="sw", font=Font(weight="bold", size=10))
        projectLabel.pack()


    def submit_time_entries(self):
        for key in self.submitDatas:
            issueId = self.submitDatas[key]["issue_id"]
            spendOn = self.submitDatas[key]["spent_on"]
            activityId = self.submitDatas[key]["activity_id"]
            hours = self.submitDatas[key]["hours"]
            comments = self.submitDatas[key]["comments"]
            if activityId >= 0 and hours and float(hours) >= 0:
                self.root.redmine.time_entry.create(
                    issue_id=issueId,
                    spend_on=spendOn,
                    hours=hours,
                    activity_id=activityId,
                    comments=comments
                )
        self.reload_time_entries()


    def reload_time_entries(self):
        self.myissuesScroll.destroy()
        self.myissuesListFrame.destroy()
        self.myissuesListCanvas.destroy()
        self.myissuesButtons.destroy()
        self.myissues_list()