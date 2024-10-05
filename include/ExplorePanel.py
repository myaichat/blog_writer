
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



         
      

class ExplorePanel(wx.Panel,Sections_Controller):
    def __init__(self, parent):
        super().__init__(parent)
        Sections_Controller.__init__(self)
        print("ExplorePanel: Sections_Controller init")
    
        # Create the WebView control
        self.web_view = wx.html2.WebView.New(self)
        
        # Attach custom scheme handler
        #self.attach_custom_scheme_handler()

        # Bind navigation and error events
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigating)
        
        #self.web_view.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.on_webview_error)
        if 1:
            # Set initial HTML content
            #pp(self.title.titles)
            #e()
            self.titles=self.title.get_titles()
            if not self.titles:
                self.set_initial_content()
            else:
                
                self.display_html()
                wx.CallAfter(log, f"ExplorePanel: Titles loaded: {len(self.titles)}")  
        # Create sizer to organize the WebView
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.web_view, 1, wx.EXPAND,0)
        self.SetSizer(sizer)
        print("ExplorePanel initialized")


    def set_initial_content(self, hard_reset=False):
        self.title.reset(hard_reset)
        self.titles=self.title.titles 
        self.topic.reset(hard_reset)  
        self.topics=self.topic.topics 
        self.section.reset(hard_reset)  
        self.sections=self.section.sections 
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
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1>Welcome to the Blog Writer</h1>
                <label><input type="checkbox" id="terms-checkbox">Mock</label>
            </div>
    
            <div id="input-container">
            <textarea id="user-input" placeholder="Enter your prompt here">%s</textarea>
            </div>
            <div id="input-container"><button id="start-button" onclick="startButtonClicked()">Get Titles</button></div>
            <br><br><br>
            <div id="output"></div>
            <script>
                function startButtonClicked() {
                    var userInput = document.getElementById('user-input').value;
                    var checkboxChecked = document.getElementById('terms-checkbox').checked;
                    document.getElementById('output').innerHTML = 'You entered: ' + userInput;
                    window.location.href = 'app:show_titles:'+checkboxChecked+ '|' + encodeURIComponent(userInput);
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
                tid=tid
                print(f"Title ID: {tid}")
                assert len(apc.titles)>int(tid)
                log(f"Using title: {apc.titles[tid]}")
                pub.sendMessage("use_title", tid=tid)
            if type == "use_topic":
                title_id,topic_id=tid.split("_")
                title_id,topic_id= title_id, topic_id
                print(f"Title ID: {title_id}")
                assert len(apc.titles)>int(title_id)
                try:
                    log(f"Using topic: {apc.topics[title_id][topic_id]}")
                except:
                    pp(apc.topics)
                    raise
                pub.sendMessage("use_topic", tid=title_id, toid=topic_id)
            if type == "use_section":
                title_id,topic_id, section_id=tid.split("_")
                title_id,topic_id, section_id= title_id, topic_id, section_id
                print(f"Title ID: {title_id}")
                assert len(apc.titles)>int(title_id)
                log(f"Using section: {apc.sections[title_id][topic_id][section_id]}")
                pub.sendMessage("use_section", tid=title_id, toid=topic_id, sid=section_id)
            elif type == "show_titles":
                mock,user_input=tid.split("|")
                print(user_input)
                apc.mock=False
                if mock=="true":
                    apc.mock=True
                log(f"design start: {mock}")
                pub.sendMessage("set_titles", user_input=user_input)

            elif type == "show_topics":
                tid=tid
                apc.expanded_title=tid
                print(f"Title ID: {tid}")
                pub.sendMessage("set_topics", title_id=tid)  
            elif type == "show_titles1":
                #tid=tid
                #apc.active_title=tid
                print(f"Get new title set")
                pub.sendMessage("set_titles")                  

            elif type == "show_sections":
                title_id,topic_id=tid.split("_")
                title_id,topic_id= title_id, topic_id
                apc.expanded_title=title_id
                apc.expanded_topic=topic_id
                print(f"Title ID: {title_id}, Topic ID: {topic_id}")
                pub.sendMessage("set_sections", title_id=title_id, topic_id=topic_id)  

            elif type == "reset_titles":
                self.set_initial_content(hard_reset=True)  

            elif type == "preview":
                print(f"preview")
                pub.sendMessage("show_preview_tab")

            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")


