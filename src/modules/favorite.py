# favorite.py
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter.font import *
from tkinter import ttk
from tkcalendar import DateEntry

class Favorite:
    # 지켜보기 일감 소요시간 입력
    def execute(self, root):
        self.root = root
        self.root.master.geometry("1120x420+100+100")
        self.root.mainFrame.config(relief="solid", bd=2)
        self.searchStatus = "*"
        self.searchStatusIndex = 0
        self.favorite_list_input_timeentries()

    def favorite_list_input_timeentries(self):
        if self.root.redmine:
            issues = self.root.redmine.issue.filter(status_id=self.searchStatus, watcher_id="me")
            self.submitDatas = {}
            # 스크롤바를 위한 캔버스
            self.favoriteListCanvas = Canvas(self.root.mainFrame, width=1070, height=340)
            self.favoriteListCanvas.grid(column=0, row=2, sticky="news")
            # 스크롤바
            self.favoriteScroll = Scrollbar(self.root.mainFrame, orient="vertical", command=self.favoriteListCanvas.yview)
            self.favoriteScroll.grid(column=3, row=2, sticky='ns')
            self.favoriteListCanvas.configure(yscrollcommand=self.favoriteScroll.set)
            # 리스트 프레임
            self.favoriteListFrame = Frame(self.favoriteListCanvas)
            self.favoriteListCanvas.create_window((0,0), window=self.favoriteListFrame, anchor="nw")
            # 마우스 휠
            def scrollMouseWheel(event):
                self.favoriteListCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            self.favoriteListCanvas.bind_all("<MouseWheel>", scrollMouseWheel)
            # 목록 헤더
            self.favorite_list_header()
            # 목록 데이터
            for i in range(len(issues)):
                issue = issues[i]
                self.favorite_list_item(issue, i+1)

            # 하단 버튼들
            self.favoriteButtons = Frame(self.root.master)
            self.favoriteButtons.pack(side=BOTTOM, pady=10)
            ## 등록버튼
            submitTimeEntries = Button(self.favoriteButtons, text="등록", command=self.submit_time_entries, width=30)
            submitTimeEntries.grid(column=0, row=0, padx=30)
            ## 조회버튼
            self.search_status_combobox()

            reloadTimeEntries = Button(self.favoriteButtons, text="조회", command=self.reload_time_entries, width=30)
            reloadTimeEntries.grid(column=2, row=0)
            ## 홈으로 이동
            homeBtn = Button(self.favoriteButtons, text="홈 으로...", command=self.move_home, width=30)
            homeBtn.grid(column=3, row=0, padx=50)

            self.favoriteListCanvas.config(scrollregion=self.favoriteListCanvas.bbox("all"))


    def search_status_combobox(self):
        optionNames = ("전체", "진행", "완료")
        optionValues = ["*", "open", "closed"]
        comboboxSV = StringVar()
        combobox = ttk.Combobox(self.favoriteButtons, width=15, textvariable=comboboxSV, state="readonly")
        combobox["values"] = optionNames

        combobox.grid(column=1, row=0, padx=10)

        def init_search_statue():
            combobox.current(self.searchStatusIndex)

        def favorite_list_search_status_change(event):
            index = event.widget.current()
            self.searchStatus = optionValues[index]
            self.searchStatusIndex = index

        combobox.bind("<<ComboboxSelected>>", favorite_list_search_status_change, optionValues)

        self.root.after(0, init_search_statue)


    def move_home(self):
        self.favoriteScroll.destroy()
        self.favoriteListFrame.destroy()
        self.favoriteListCanvas.destroy()
        self.favoriteButtons.destroy()
        self.root.reload()

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
        self.favorite_list_header_label("설명", 5, 250, 42)


    def favorite_list_item_label(self, text, col, row, width, labelWidth, justify, cursor="arrow"):
        label_frame = Frame(self.favoriteListFrame, width=width, padx=10, pady=5)
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


    def favorite_list_item(self, issue, index):
        submitKey = str(issue.id) + "_" + str(index);
        # 이슈번호
        def move_issue_page(event):
            webbrowser.open_new_tab(self.root.redmine_url + "/issues/" + str(issue.id))

        issueLabel = self.favorite_list_item_label(issue.id, 0, index, 120, 10, CENTER)
        issueLabel.config(highlightcolor="#dbdbdb", font=Font(underline=True, size=9), fg="#3F48CC")
        issueLabel.bind("<Button-1>", move_issue_page)
        # 제목
        self.favorite_list_item_label(issue.subject, 1, index, 320, 40, LEFT)
        # 작업일시
        date = DateEntry(self.favoriteListFrame, values="Text", state="readonly", date_pattern="yyyy-mm-dd", width=10)
        date.grid(column=2, row=index)

        def favorite_list_item_date_change(event):
            self.submitDatas[submitKey]["spent_on"] = date.get()

        date.bind("<<DateEntrySelected>>", favorite_list_item_date_change)

        # 작업종류
        activities = issue.project.time_entry_activities
        optionNames = ["-- 선택 --"]
        optionValues = [-1]
        activityId = -1
        for activity in activities:
            optionNames.append(activity["name"])
            optionValues.append(activity["id"])
        n = StringVar()
        combobox = ttk.Combobox(self.favoriteListFrame, width=15, textvariable=n, state="readonly")
        combobox["values"] = optionNames

        combobox.grid(column=3, row=index)
        combobox.current()
        def init_combobox():
            combobox.current(0)

        self.root.after(0, init_combobox)

        def favorite_list_item_combobox_change(event):
            index = event.widget.current()
            activityId = optionValues[index]
            self.submitDatas[submitKey]["activity_id"] = activityId

        combobox.bind("<<ComboboxSelected>>", favorite_list_item_combobox_change, optionValues)

        # 소요시간
        timeSV = StringVar()
        def favorite_list_item_time_input(*args):
            self.submitDatas[submitKey]["hours"] = timeSV.get()

        timeSV.trace("w", favorite_list_item_time_input)
        time = Entry(self.favoriteListFrame, width=10, textvariable=timeSV)
        time.grid(column=4, row=index)

        # 설명
        commentsSV = StringVar()
        def favorite_list_item_comments_input(*args):
            self.submitDatas[submitKey]["comments"] = commentsSV.get()

        commentsSV.trace("w", favorite_list_item_comments_input)
        comments = Entry(self.favoriteListFrame, width=40, textvariable=commentsSV)
        comments.grid(column=5, row=index)

        # 등록 데이터 초기화
        self.submitDatas[submitKey] = {
            "issue_id": issue.id,
            "spent_on": date.get(),
            "activity_id": activityId,
            "hours": None,
            "comments": None
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
            comments = self.submitDatas[key]["comments"]
            if activityId >= 0 and hours and int(hours) >= 0:
                self.root.redmine.time_entry.create(
                    issue_id=issueId,
                    spend_on=spendOn,
                    hours=hours,
                    activity_id=activityId,
                    comments=comments
                )
        self.reload_time_entries()


    def reload_time_entries(self):
        self.favoriteScroll.destroy()
        self.favoriteListFrame.destroy()
        self.favoriteListCanvas.destroy()
        self.favoriteButtons.destroy()
        self.favorite_list_input_timeentries()