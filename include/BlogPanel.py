import wx
from pubsub import pub
class Titles():
    def __init__(self):
        self.set_blog()

    def set_blog(self):
        self.blog = {'title': ''}

    def get_blog(self):
        return self.blog

    def __repr__(self):
        return self.blog
class Blog_Controller():  
    def __init__(self):
        self.blog = Titles()
        pub.subscribe(self.use_title, "use_title")
    def  use_title(self, tid):
        print(f"Using title: {tid}")
        blog = self.blog.get_blog()
        blog['title'] = str(tid)
        
        blog_html= "<table>"
        for sid, section in blog.items():
            blog_html += f'<tr><td><button onclick="testButtonClicked({sid})"></button></td><td>{section}</td></tr>'
        blog_html += "</table>"

        new_html = """
        <html>
        <body>
            <h1>Blog</h1>
            %s
            <button onclick="testButtonClicked()">New</button>
            <br><br>
            <a href="app:url_test">Click this URL</a>
            
            <script>
                function testButtonClicked(tid) {
                    console.log('Test button clicked', tid);
                    window.location.href = 'app:titles:'+tid;
                }
            </script>
        </body>
        </html>
        """ % blog_html
        self.web_view.SetPage(new_html, "")
    def set_titles(self):
        titles = self.titles.get_titles()
        print(f"Titles: {titles}")
        titles_html= "<table>"
        for tid, title in enumerate(titles):
            titles_html += f'<tr><td><button onclick="testButtonClicked({tid})"><<<</button></td><td>{title}</td></tr>'
        titles_html += "</table>"

        new_html = """
        <html>
        <body>
            <h1>Titles</h1>
            %s
            <button onclick="testButtonClicked()">New</button>
            <br><br>
            <a href="app:url_test">Click this URL</a>
            
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

class Blog_WebViewPanel(wx.Panel, Blog_Controller):
    def __init__(self, parent):
        super().__init__(parent)
        Blog_Controller.__init__(self)
        
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
        handler = CustomSchemeHandler_Blog(self)
        self.web_view.RegisterHandler(handler)

    def set_initial_content(self):
        initial_html = """
        <html>
        <body>
            <h1>Blog!</h1>
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
        initial_html = """
        <html>
        <body>
            <pre>Get titles first >>></pre>

        </body>
        </html>
        """        
        self.web_view.SetPage(initial_html, "")



    def on_navigating(self, event):
        url = event.GetURL()
        print(f"Blog Navigating to: {url}")
        if url.startswith("app:"):
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")

class CustomSchemeHandler_Blog(wx.html2.WebViewHandler):
    def __init__(self, web_view_panel):
        wx.html2.WebViewHandler.__init__(self, "app")
        self.web_view_panel = web_view_panel

    def OnRequest(self, webview, request):
        print(f"OnRequest called with URL: {request.GetURL()}")
        if request.GetResourceType() == wx.html2.WEBVIEW_RESOURCE_TYPE_MAIN_FRAME:
            if request.GetURL() == "app:test":
                wx.CallAfter(self.web_view_panel.on_test_button)
            elif request.GetURL() == "app:url_test":
                wx.CallAfter(self.web_view_panel.on_url_test)
        return None

class BlogPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = Blog_WebViewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "Blog")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)