import wx
import wx.html2
from pubsub import pub
from include.BlogPanel import BlogPanel
from include.LogPanel import LogPanel 
from include.DesignPanel import DesignPanel  
from include.PreviewPanel import PreviewPanel
import include.config.init_config as init_config 

init_config.init(**{})
apc = init_config.apc

apc.mock = True


class WorkbookPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.design_web_view_panel = DesignPanel(self.notebook)
        self.preview_web_view_panel = PreviewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.design_web_view_panel, "Explore")
        self.notebook.AddPage(self.preview_web_view_panel, "Preview")
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
        pub.subscribe(self.show_explore_tab, "show_explore_tab")
        pub.subscribe(self.show_preview_tab, "show_preview_tab")
    def show_explore_tab(self):
        self.notebook.SetSelection(0)
    def show_preview_tab(self):
        self.notebook.SetSelection(1)   
    def on_get_titles(self, event):
        #self.text_ctrl.AppendText("Get Titles button clicked!\n")
        #self.web_view_panel.update_html_content()
        pub.sendMessage("set_titles")






# Main Application with WebViewPanel, TextCtrl, and Chat Button
class MyApp(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Blog Writer')
        self.config = wx.Config("MyAppSettings")
        panel = wx.Panel(self)
        
        blog_panel = BlogPanel(panel)
        blog_panel.SetMinSize((500, -1))
        #self.notebook.AddPage(blog_panel, "Blog")
        design_panel = WorkbookPanel(panel)
        log_panel = LogPanel(panel)
        log_panel.SetMinSize((400, -1))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(blog_panel, 0, wx.EXPAND, 0)
        sizer.Add(design_panel, 1, wx.EXPAND,0)
        sizer.Add(log_panel, 0, wx.EXPAND,0)
        panel.SetSizer(sizer)

        
        self.restore_layout()

        # Bind the close event to save the layout when the window is closed
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()
    def restore_layout(self):
        """Restore the layout and UI component states using wx.Config."""
        size = self.config.Read("window_size", "800,600").split(',')
        position = self.config.Read("window_position", "50,50").split(',')
        text_value = self.config.Read("text_ctrl_value", "Default text")

        # Restore window size and position
        self.SetSize((int(size[0]), int(size[1])))
        self.SetPosition((int(position[0]), int(position[1])))
    def on_close(self, event):
        """Save layout and UI component states using wx.Config."""
        size = self.GetSize()
        position = self.GetPosition()

        self.config.Write("window_size", f"{size[0]},{size[1]}")
        self.config.Write("window_position", f"{position[0]},{position[1]}")
        
        
        #self.config.WriteInt("splitter_position", self.splitter.GetSashPosition())

        self.config.Flush()  # Ensure the config data is written to disk

        # Proceed with closing the window
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = MyApp()
    app.MainLoop()
