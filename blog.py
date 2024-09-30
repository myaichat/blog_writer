import wx
import wx.html2
from pubsub import pub
from include.BlogPanel import BlogPanel
from include.LogPanel import LogPanel 
from include.TitlePanel import TitlePanel  
import include.config.init_config as init_config 

init_config.init(**{})
apc = init_config.apc




class DesignPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = TitlePanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "Design")
        if 0:
            chat_sizer = wx.BoxSizer(wx.HORIZONTAL)
            # Create a multiline TextCtrl (read-only)
            self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(300, 100))
            self.text_ctrl.AppendText("DeepLearning.AI\n")
            # Create a "Chat" button
            get_titles_button = wx.Button(panel, label='Start')
            get_titles_button.Bind(wx.EVT_BUTTON, self.on_get_titles)
            chat_sizer.Add(self.text_ctrl, 0, wx.EXPAND | wx.ALL, 5)
            chat_sizer.Add(get_titles_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        # Create sizer to manage layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        #main_sizer.Add(chat_sizer, 0, wx.EXPAND | wx.ALL, 5)


        panel.SetSizer(main_sizer)
    def on_get_titles(self, event):
        #self.text_ctrl.AppendText("Get Titles button clicked!\n")
        #self.web_view_panel.update_html_content()
        pub.sendMessage("set_titles")






# Main Application with WebViewPanel, TextCtrl, and Chat Button
class MyApp(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Blog Designer')
        panel = wx.Panel(self)
        
        self.blog_panel = BlogPanel(panel)
        #self.notebook.AddPage(blog_panel, "Blog")
        design_panel = DesignPanel(panel)
        log_panel = LogPanel(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.blog_panel, 1, wx.EXPAND)
        sizer.Add(design_panel, 1, wx.EXPAND)
        sizer.Add(log_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        

        self.SetSize((1200, 1000))
        self.Show()



if __name__ == '__main__':
    app = wx.App()
    frame = MyApp()
    app.MainLoop()
