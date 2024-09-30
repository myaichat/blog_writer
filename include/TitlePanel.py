
import wx
from pubsub import pub
import include.config.init_config as init_config 

apc = init_config.apc
class Titles():
    def __init__(self):
        self.set_titles()

    def set_titles(self):
        self.titles = [ "Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI",
        "Empowering the Next Generation: DeepLearning.AI's Role in AI Education and Workforce Development",
        "Leading the Way: Groundbreaking Research and Innovations from DeepLearning.AI",
        "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI",
        "Ethics in AI: DeepLearning.AI's Journey Towards Responsible and Fair Artificial Intelligence"]
        apc.titles=self.titles

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
        titles_html= """<h3 class="left-align"> Generated:</h3>
<table>"""
        for tid, title in enumerate(titles):
            titles_html += f'<tr><td><button onclick="testButtonClicked({tid})"><<<</button></td><td>{title}</td></tr>'
        titles_html += "</table>"

        new_html = """
        <html>
       <head>
           <style>
                .left-align {
                    text-align: left;
                }
     
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

class TitlePanel(wx.Panel,Titles_Controller):
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
                tid=int(tid)
                print(f"Title ID: {tid}")
                assert len(apc.titles)>tid
                pub.sendMessage("applog", log=f"Selected title: {apc.titles[tid]}")
                pub.sendMessage("use_title", tid=tid)
            elif type == "start":
                pub.sendMessage("applog", log="design start")
                pub.sendMessage("set_titles")
            elif type == "show_start":
                self.set_initial_content()                
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")


