import wx
import wx.html2
from pubsub import pub
from include.BlogPanel import BlogPanel
from include.LogPanel import LogPanel   

class Titles():
    def __init__(self):
        self.set_titles()

    def set_titles(self):
        self.titles = [ "Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI",
        "Empowering the Next Generation: DeepLearning.AI's Role in AI Education and Workforce Development",
        "Leading the Way: Groundbreaking Research and Innovations from DeepLearning.AI",
        "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI",
        "Ethics in AI: DeepLearning.AI's Journey Towards Responsible and Fair Artificial Intelligence"]

    def get_titles(self):
        return self.titles

    def __repr__(self):
        return self.titles
    
class Titles_Controller():  
    def __init__(self):
        self.titles = Titles()
        pub.subscribe(self.set_titles, "set_titles")

    def set_titles(self):
        titles = self.titles.get_titles()
        print(f"Titles: {titles}")
        titles_html= "<table>"
        for tid, title in enumerate(titles):
            titles_html += f'<tr><td><button onclick="testButtonClicked({tid})"><<<</button></td><td>{title}</td></tr>'
        titles_html += "</table>"

        new_html = """
        <html>
       <head>
            <style>
                body { font-family: Arial, sans-serif; }
                #header-container {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }
                #header-container h1 {
                    margin: 0;
                }
                #url-input {
                    width: 300px;
                    padding: 5px;
                }
                #input-container { margin: 20px 0; }
                #user-input {
                    width: 300px;
                    height: 100px;
                    padding: 5px;
                    resize: vertical;
                }
                #start-button { padding: 5px 10px; vertical-align: top; }
            </style>
        </head>        
        <body>
            <pre>
                <div id="header-container">
                <h1>Titles</h1>
                <a href="app:show_start:0">Reset</a>
            </div>
            %s
            
            <br><br>
            
            </pre>
            <script>
                function testButtonClicked(tid) {
                    console.log('Test button clicked', tid);
                    window.location.href = 'app:titles:'+tid;
                }
            </script>
        </body>
        </html>
        """ % titles_html
        self.web_view.SetPage(new_html, "")        

class Titles_WebViewPanel(wx.Panel,Titles_Controller):
    def __init__(self, parent):
        super().__init__(parent)
        Titles_Controller.__init__(self)
        # Create the WebView control
        self.web_view = wx.html2.WebView.New(self)

        # Attach custom scheme handler
        #self.attach_custom_scheme_handler()

        # Bind navigation and error events
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigating)
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.on_webview_error)

        # Set initial HTML content
        self.set_initial_content()

        # Create sizer to organize the WebView
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.web_view, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def set_initial_content(self):
        initial_html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                #input-container { margin: 20px 0; }
                #user-input {
                    width: 300px;
                    height: 100px;
                    padding: 5px;
                    resize: vertical;
                }
                #start-button { padding: 5px 10px; vertical-align: top; }
            </style>
        </head>
        <body>
            <h1>Welcome to the Blog Designer</h1>
            <div id="input-container">
                <textarea id="user-input" placeholder="Enter your prompt here">Deeplearning.AI</textarea>
                
            </div>
            <div id="button"><button id="start-button" onclick="startButtonClicked()">Get Titles</button></div>
            <br><br><br>
            <div id="output"></div>
            <script>
                function startButtonClicked() {
                    var userInput = document.getElementById('user-input').value;
                    document.getElementById('output').innerHTML = 'You entered: ' + userInput;
                    window.location.href = 'app:start:0' + encodeURIComponent(userInput);
                }
            </script>
        </body>
        </html>
        """
        self.web_view.SetPage(initial_html, "")



    def on_navigating(self, event):
        url = event.GetURL()
        print(f"BLOG: Navigating to: {url}")
        if url.startswith("app:"):
            _, type,tid = url.split(":")
            if type == "titles":
                print(f"Title ID: {tid}")
                pub.sendMessage("use_title", tid=tid)
            elif type == "start":
                pub.sendMessage("set_titles")
            elif type == "show_start":
                self.set_initial_content()                
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")





class DesignPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = Titles_WebViewPanel(self.notebook)

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
