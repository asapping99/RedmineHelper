import wx
import wx.html2 as webview


class WebBrowse(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        parent = webview.WebView.New(self)

if __name__ == '__main__':
    print("webkit...")