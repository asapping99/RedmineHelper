import os
from tkinter import *
import tkinter.messagebox as alert
from redminelib import Redmine
import json
from modules.favorite import Favorite
from modules.mypage import MyPage
from configuration.config import Config

user_json_path = "./user_info.json"

class Main(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.pack_propagate(0)
        self.pack()
        self.initPage = 1
        self.execute(self)

    @staticmethod
    def execute(self):
        #with open("configuration.json", "r") as f:
        #    self.jsonData = json.load(f)
        self.make_window()

    def reload(self):
        self.mainFrame.destroy()
        self.make_window()

    def make_window(self):
        self.master.title("레드마인 도우미")
        self.master.geometry("800x420+100+100")
        # self.master.geometry("400x140+100+100")
        self.master.resizable(False, False)

        self.mainFrame = Frame(self.master)

        # scrollbar = Scrollbar(self.mainFrame, orient="vertical")
        # scrollbar.pack(side="right", fill="y")
        # 설정 초기화
        self.configuration()
        # 사용자 정보
        self.user_info()

        # 홈
        if self.redmine:
            self.homeFrame = None
            if self.initPage == 1:
                self.initPage = 0
                self.move_mypage()
            else:
                self.make_home()

        self.mainFrame.pack()


    def configuration(self):
        if os.path.exists(user_json_path):
            self.redmine_url = Config().constants["server_url"]
            with open(user_json_path, "r") as json_file:
                self.json_data = json.load(json_file)
            if self.json_data['apiKey']:
                apiKey = self.json_data['apiKey']
                self.redmine = Redmine(self.redmine_url, key=apiKey)
        else:
            self.json_data = None
            self.redmine = None
            self.redmine_url = None

    def make_home(self):
        self.homeFrame = Frame(self.mainFrame.master)
        self.homeFrame.pack()
        mypageBtn = Button(self.homeFrame, text="내 페이지", command=self.move_mypage, width=30)
        mypageBtn.grid(column=1, row=0, padx=10, pady=10)
        favoriteBtn = Button(self.homeFrame, text="지켜보고 있는 일감\n소요시간 등록", command=self.move_favorite, width=30)
        favoriteBtn.grid(column=2, row=0, padx=10, pady=10)

    # 내 페이지
    def move_mypage(self):
        MyPage().execute(self, self.redmine_url, self.json_data)
        if self.homeFrame:
            self.homeFrame.destroy()

    # 지켜보고 있는 일감 소요시간 등록
    def move_favorite(self):
        Favorite().execute(self)
        self.homeFrame.destroy()

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
            label = Label(self.mainFrame, text="사용자 명")
            label.grid(column=0, row=0, pady=5)

            self.userName = StringVar()
            self.textboxUserName = Entry(self.mainFrame, width=12, textvariable=self.userName)
            self.textboxUserName.grid(column=1, row=0, padx=5, pady=5)

            label = Label(self.mainFrame, text="API Key")
            label.grid(column=2, row=0, pady=5)

            self.apiKey = StringVar()
            self.textboxApiKey = Entry(self.mainFrame, width=12, textvariable=self.apiKey)
            self.textboxApiKey.grid(column=3, row=0, padx=10, pady=5)

            self.button = Button(self.mainFrame, text="저장", command=self.saveUserInfo)
            self.button.grid(column=4, row=0, padx=5, pady=10)



if __name__ == '__main__':
    root = Tk()
    root.iconbitmap(Config().constants["icon"])
    main_window = Main(master=root)
    root.mainloop()