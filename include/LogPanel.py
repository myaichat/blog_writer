import wx
class Log_WebViewPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        
        # Create the WebView control
        self.web_view = wx.html2.WebView.New(self)
        
        # Attach custom scheme handler
        self.attach_custom_scheme_handler()

        # Bind navigation and error events
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigating)
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.on_webview_error)

        # Set initial HTML content
        self.set_initial_content()

        # Create sizer to organize the WebView
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.web_view, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def attach_custom_scheme_handler(self):
        handler = CustomSchemeHandler_Log(self)
        self.web_view.RegisterHandler(handler)

    def set_initial_content(self):
        initial_html = """
        <html>
        <body>
            <h1>App Log</h1>
            <button onclick="testButtonClicked()">Test Button</button>
            <br><br>
            <a href="app:url_test">Click this URL</a>
            <script>
                function testButtonClicked() {
                    console.log('Test button clicked');
                    window.location.href = 'app:test';
                }
            </script>
        </body>
        </html>
        """
        self.web_view.SetPage(initial_html, "")



    def on_navigating(self, event):
        url = event.GetURL()
        print(f"Log Navigating to: {url}")
        if url.startswith("app:"):
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")

class CustomSchemeHandler_Log(wx.html2.WebViewHandler):
    def __init__(self, web_view_panel):
        wx.html2.WebViewHandler.__init__(self, "app")
        self.web_view_panel = web_view_panel

    def OnRequest(self, webview, request):
        print(f"Log: OnRequest called with URL: {request.GetURL()}")
        if request.GetResourceType() == wx.html2.WEBVIEW_RESOURCE_TYPE_MAIN_FRAME:
            if request.GetURL() == "app:test":
                wx.CallAfter(self.web_view_panel.on_test_button)
            elif request.GetURL() == "app:url_test":
                wx.CallAfter(self.web_view_panel.on_url_test)
        return None

class LogPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = Log_WebViewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "App Log")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
