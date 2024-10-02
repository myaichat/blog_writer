import wx
import wx.html2

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(800, 600))

        # Create a WebView
        self.browser = wx.html2.WebView.New(self)
        
        # Bind the webview navigation event
        self.browser.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigation_request)

        # Load the HTML content
        self.browser.SetPage(self.get_html(), "")

    def get_html(self):
        # The HTML content, including the button click logic
        return """
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
                <h1>Blog</h1>
                <div id="button">Start with <button id="activate-button" onclick="startButtonClicked()">Exploration</button></div>
                <div id="output"></div>
                <script>
                    function startButtonClicked() {
                        console.log('Start button clicked');
                        window.location.href = 'app:explore';  // Trigger the navigation event
                    }
                </script>
            </body>
        </html>
        """

    def on_navigation_request(self, event):
        url = event.GetURL()
        
        # Check if the custom scheme 'app:' is used
        if url.startswith("app:explore"):
            event.Veto()  # Stop the browser from navigating away
            wx.MessageBox("Button clicked, action intercepted in Python!", "Info")
            # Add your Python logic here
        else:
            event.Skip()  # Allow normal navigation for other URLs

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, title="WebView Button Click Example")
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
