import wx
from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Design import Design_Controller
import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log
apc.used_section=None
apc.used_section    =None
class Design_WebViewPanel(wx.Panel, Design_Controller):
    def __init__(self, parent,):
        super().__init__(parent)
        Design_Controller.__init__(self)
        
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
        sizer.Add(self.web_view, 1, wx.EXPAND,0)
        self.SetSizer(sizer)


        


    def set_initial_content(self):
        initial_html = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    #activate-button { 
                        padding: 2px 5px;
                        font-size: 16px;
                        cursor: pointer;
                        background-color: #90EE90;
                        color: black;
                        border: none;
                        border-radius: 2px;
                    }
                </style>
            </head>
            <body>
                <h1>Design</h1>
                <div id="button">Start with <button id="activate-button" onclick="startButtonClicked()">Exploration</button> --->>></div>
                <div id="output"></div>
                <script>
                    function startButtonClicked() {
                        console.log('Start button clicked');
                        window.location.href = 'app:explore:0';  // Trigger the navigation event
                    }
                </script>
            </body>
        </html>
        """  
        self.web_view.SetPage(initial_html, "")
    def decode(self, encoded_string):
        import urllib.parse

        # The encoded URL string
        #encoded_string = "Transforming%20Industries%3A%20How%20DeepLearning.AI%20is%20Revolutionizing%20Business%20with%20AI"

        # Decode the string
        decoded_string = urllib.parse.unquote(encoded_string)
        return decoded_string


    def on_navigating(self, event):
        url = event.GetURL()
        print(f"Blog Navigating to: {url[:50]}")
        if url.startswith("app:"):
            _, type,payload = url.split(":")
            if type == "explore":
                pub.sendMessage("show_explore_tab")  
            if type == "show_preview":
                pub.sendMessage("show_preview_tab")                  
                          
            if type == "set_title":
                title= self.decode(payload)
                print(f"Setting title: {title}")
            if type == "reset_design":
                title= self.decode(payload)
                print(f"Resetting design: {title}") 
                self.design.reset(hard=True) 
                self.set_initial_content()  
            if type == "activate_topic":
                tid, toid = payload.split("_")
                tid, toid = int(tid), int(toid)
                #title= self.decode(payload)
                print(f"activate_topic: {tid, toid}")
                self.activate_topic(tid, toid)   
            if type == "activate_section":
                tid, toid, sid = payload.split("_")
                tid, toid, sid = int(tid), int(toid), int(sid)
                #title= self.decode(payload)
                print(f"activate_section: {tid, toid, sid}")
                self.activate_section(tid, toid, sid)             
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
        self.web_view_panel = Design_WebViewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "Design")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)