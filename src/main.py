import webbrowser
#import json
from tkinter import *
import config.config as Config

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

    def openClicked(self):
        issueNo = self.textboxIssueNo.get()
        if issueNo is None or issueNo == "":
            self.errorMsg.set("이슈번호를 입력해 주세요.")
        else:
            self.errorMsg.set("")
            self.issueNo.set("")
            webbrowser.open_new_tab(Config.CONFIG_CONSTANTS["server_url"]+"/issues/"+issueNo)
            #webbrowser.open_new_tab(self.jsonData["server_url"] + "/issues/" + issueNo)

    def make_window(self):
        self.master.title("레드마인 도우미")
        self.master.geometry("300x80+100+100")
        self.master.resizable(False, False)

        label = Label(self, text="이슈번호")
        label.grid(column=0, row=0, pady=10)
        #label.grid(column=0, row=0)

        reg = root.register(self.limit)
        self.issueNo = StringVar()
        self.textboxIssueNo = Entry(self, width=12, textvariable=self.issueNo, validate='key', validatecommand=(reg, '%P'))
        self.textboxIssueNo.grid(column=1, row=0, padx=5, pady=10)
        self.textboxIssueNo.focus()
        self.textboxIssueNo.bind("<Return>", self.on_enterkey)

        self.button = Button(self, text="열기", command=self.openClicked)
        self.button.grid(column=2, row=0, padx=5, pady=10)

        self.errorMsg = StringVar()
        self.errorLabel = Label(self, textvariable=self.errorMsg, fg="red")
        self.errorLabel.grid(column=0, row=1, columnspan=3)

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
    root.iconbitmap(Config.CONFIG_CONSTANTS["project_dir"] + "/icon/icon.ico")
    main_window = Main(master=root)
    root.mainloop()