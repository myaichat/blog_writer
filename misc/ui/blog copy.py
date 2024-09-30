import wx
import wx.html

class CustomHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.set_initial_content()

    def set_initial_content(self):
        html_content = """
        <html>
        <body>
            <h1>Welcome to the Chat App!</h1>
            <form>
                <input type="button" value="Test Button" onclick="wx.PostEvent(window, wx.CommandEvent(wx.wxEVT_BUTTON, 100))">
            </form>
            <br>
            <a href="url_test">Click this URL</a>
        </body>
        </html>
        """
        self.SetPage(html_content)

    def OnLinkClicked(self, link):
        href = link.GetHref()
        if href == "url_test":
            wx.PostEvent(self, CustomHtmlEvent(EVT_URL_TEST.typeId, self.GetId()))

class CustomHtmlEvent(wx.PyCommandEvent):
    def __init__(self, evt_type, id):
        super().__init__(evt_type, id)

# Define custom event types
EVT_URL_TEST = wx.NewEventType()

# Create event binders
EVT_URL_TEST = wx.PyEventBinder(EVT_URL_TEST, 1)

class ChatApp(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Chat Application')
        panel = wx.Panel(self)

        # Create a notebook
        self.notebook = wx.Notebook(panel)

        # Create "Titles" tab with CustomHtmlWindow
        titles_panel = wx.Panel(self.notebook)
        self.html_window = CustomHtmlWindow(titles_panel)
        titles_sizer = wx.BoxSizer(wx.VERTICAL)
        titles_sizer.Add(self.html_window, 1, wx.EXPAND | wx.ALL, 10)
        titles_panel.SetSizer(titles_sizer)

        # Add "Titles" tab to notebook
        self.notebook.AddPage(titles_panel, "Titles")

        # Bind custom events
        self.html_window.Bind(wx.EVT_BUTTON, self.on_test_button)
        self.Bind(EVT_URL_TEST, self.on_url_test)

        # Create a multiline text control
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Create a "Chat" button
        chat_button = wx.Button(panel, label='Chat')
        chat_button.Bind(wx.EVT_BUTTON, self.on_chat)

        # Create sizer to organize the widgets
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(chat_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)
        self.SetSize((600, 600))
        self.Show()

    def on_chat(self, event):
        self.text_ctrl.AppendText("Chat button clicked!\n")

    def on_test_button(self, event):
        self.text_ctrl.AppendText("Test button in HTML window clicked!\n")
        wx.MessageBox("Test button clicked!", "Info", wx.OK | wx.ICON_INFORMATION)

    def on_url_test(self, event):
        self.text_ctrl.AppendText("URL in HTML window clicked!\n")
        wx.MessageBox("URL clicked!", "Info", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App()
    frame = ChatApp()
    app.MainLoop()