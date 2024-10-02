
import wx
from pubsub import pub
from pprint import pprint as pp
import include.config.init_config as init_config 

from include.Controller.Sections import Sections_Controller
apc = init_config.apc
log=apc.log
apc.prompt = "Deeplearning.AI"
apc.expanded_title=None
apc.expanded_topic=None



         
      

class DesignPanel(wx.Panel,Sections_Controller):
    def __init__(self, parent):
        super().__init__(parent)
        Sections_Controller.__init__(self)
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
        self.title.reset()
        self.topic.reset()
        self.section.reset()
        initial_html = """
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
                #input-container { 
                    margin: 20px 0;
                    display: flex;
                    align-items: flex-start;
                }
                #user-input {
                    width: 300px;
                    height: 100px;
                    padding: 5px;
                    resize: vertical;
                    margin-right: 10px;
                }
                #start-button { 
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                #start-button:hover {
                    background-color: #45a049;
                }
  #input-container {
      width: 100%%;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
  }

  #user-input {
      width: 100%%;
      height: 200px;
      padding: 10px;
      font-size: 16px;
      border: 2px solid #ccc;
      border-radius: 8px;
      box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
      resize: vertical;
      line-height: 1.5;
  }                
            </style>
        </head>
        <body>
            <h1>Welcome to the Blog Writer</h1>
            <div id="input-container">
            <textarea id="user-input" placeholder="Enter your prompt here">%s</textarea>
            </div>
            <div id="input-container"><button id="start-button" onclick="startButtonClicked()">Get Titles</button></div>
            <br><br><br>
            <div id="output"></div>
            <script>
                function startButtonClicked() {
                    var userInput = document.getElementById('user-input').value;
                    document.getElementById('output').innerHTML = 'You entered: ' + userInput;
                    window.location.href = 'app:start:' + encodeURIComponent(userInput);
                }
            </script>
        </body>
        </html>
        """ % apc.prompt
        self.web_view.SetPage(initial_html, "")



    def on_navigating(self, event):
        url = event.GetURL()
        print(f"BLOG: Navigating to: {url[:50]}")
        if url.startswith("app:"):
            _, type,tid = url.split(":")
            
            if type == "use_title":
                tid=int(tid)
                print(f"Title ID: {tid}")
                assert len(apc.titles)>tid
                log(f"Using title: {apc.titles[tid]}")
                pub.sendMessage("use_title", tid=tid)
            if type == "use_topic":
                title_id,topic_id=tid.split("_")
                title_id,topic_id= int(title_id), int(topic_id)
                print(f"Title ID: {title_id}")
                assert len(apc.titles)>int(title_id)
                log(f"Using topic: {apc.topics[title_id][topic_id]}")
                pub.sendMessage("use_topic", tid=int(title_id), toid=int(topic_id))
            if type == "use_section":
                title_id,topic_id, section_id=tid.split("_")
                title_id,topic_id, section_id= int(title_id), int(topic_id), int(section_id)
                print(f"Title ID: {title_id}")
                assert len(apc.titles)>int(title_id)
                log(f"Using section: {apc.sections[title_id][topic_id][section_id]}")
                pub.sendMessage("use_section", tid=int(title_id), toid=int(topic_id), sid=int(section_id))
            elif type == "start":
                user_input=tid
                log("design start")
                pub.sendMessage("set_titles", user_input=user_input)

            elif type == "show_topics":
                tid=int(tid)
                apc.expanded_title=tid
                print(f"Title ID: {tid}")
                pub.sendMessage("set_topics", title_id=tid)  

            elif type == "show_sections":
                title_id,topic_id=tid.split("_")
                title_id,topic_id= int(title_id), int(topic_id)
                apc.expanded_title=title_id
                apc.expanded_topic=topic_id
                print(f"Title ID: {title_id}, Topic ID: {topic_id}")
                pub.sendMessage("set_sections", title_id=int(title_id), topic_id=int(topic_id))  

            elif type == "show_start":
                self.set_initial_content()  

            elif type == "preview":
                print(f"preview")
                pub.sendMessage("show_preview_tab")

            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")


