import wx
import wx.html2

class WebViewPanel(wx.Panel):
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
        handler = CustomSchemeHandler(self)
        self.web_view.RegisterHandler(handler)

    def set_initial_content(self):
        initial_html = """
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
            <div id="header-container">
                <h1>Welcome to the WebView Panel!</h1>
                (<a href="app:show_start:0">Reset</a>)
            </div>
            <div id="input-container">
                <textarea id="user-input" placeholder="Enter your text here"></textarea>
                <button id="start-button" onclick="startButtonClicked()">Start</button>
            </div>
            <div id="output"></div>
            <script>
                function startButtonClicked() {
                    var userInput = document.getElementById('user-input').value;
                    var url = document.getElementById('url-input').value;
                    document.getElementById('output').innerHTML = 'You entered: ' + userInput.replace(/\\n/g, '<br>') + '<br>URL: ' + url;
                    window.location.href = 'app:start?input=' + encodeURIComponent(userInput) + '&url=' + encodeURIComponent(url);
                }
            </script>
        </body>
        </html>
        """
        self.web_view.SetPage(initial_html, "")

    def on_start_button(self, user_input, url):
        print(f"Start button clicked with input:\n{user_input}")
        print(f"URL: {url}")
        wx.MessageBox(f"You entered:\n{user_input}\n\nURL: {url}", "Input Received", wx.OK | wx.ICON_INFORMATION)

    def on_navigating(self, event):
        url = event.GetURL()
        print(f"Navigating to: {url}")
        if url.startswith("app:"):
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")

    def update_html_content(self, new_content):
        self.web_view.SetPage(new_content, "")

class CustomSchemeHandler(wx.html2.WebViewHandler):
    def __init__(self, web_view_panel):
        wx.html2.WebViewHandler.__init__(self, "app")
        self.web_view_panel = web_view_panel

    def OnRequest(self, webview, request):
        print(f"OnRequest called with URL: {request.GetURL()}")
        if request.GetResourceType() == wx.html2.WEBVIEW_RESOURCE_TYPE_MAIN_FRAME:
            url = request.GetURL()
            if url.startswith("app:start?"):
                # Extract the user input and URL from the request
                parsed_url = wx.URL(url)
                user_input = parsed_url.GetQueryParameter("input")
                input_url = parsed_url.GetQueryParameter("url")
                wx.CallAfter(self.web_view_panel.on_start_button, user_input, input_url)
        return None

class MyApp(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='WebView Panel with Chat and Notebook')

        panel = wx.Panel(self)

        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = WebViewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "Titles")

        # Create a multiline TextCtrl (read-only)
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Create a "Chat" button
        chat_button = wx.Button(panel, label='Chat')
        chat_button.Bind(wx.EVT_BUTTON, self.on_chat)

        # Create sizer to manage layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(chat_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)
        self.SetSize((800, 600))
        self.Show()

    def on_chat(self, event):
        self.text_ctrl.AppendText("Chat button clicked!\n")
        
        # Update the HTML content in the WebView
        new_html_content = """
        <html>
        <body>
            <h1>Chat Button Clicked!</h1>
            <p>This content was updated when you clicked the Chat button.</p>
            <button onclick="alert('Hello from updated content!')">Click me</button>
        </body>
        </html>
        """
        self.web_view_panel.update_html_content(new_html_content)

if __name__ == '__main__':
    app = wx.App()
    frame = MyApp()
    app.MainLoop()