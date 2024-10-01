
import wx
from pubsub import pub
from pprint import pprint as pp
import include.config.init_config as init_config 
from include.Controller.Topics import Topics_Controller
apc = init_config.apc

class Section():
    def __init__(self):
        self.sections = {}
        #self.set_topics()

    def set_sections(self, title_id, topic_id):
        self.sections[int(title_id)]={}
        self.sections[int(title_id)][int(topic_id)] = ['''### Introduction: The Vision Behind DeepLearning.AI's Community Initiatives
    At DeepLearning.AI, we envision a future where artificial intelligence 
    flourishes through collaboration and active community engagement. 
    Our mission is to cultivate a dynamic ecosystem that unites experts,
     learners, and enthusiasts alike, empowering them to share knowledge and 
    drive innovation together. By prioritizing partnerships and fostering 
    inclusive initiatives, we strive to make AI accessible and impactful for 
    everyone. In this blog, we invite you to explore the collaborative efforts 
    that are nurturing a thriving AI community and inspiring the next generation 
    of technological breakthroughs.''']  * 5
        apc.sections=self.sections


    def get_sections(self, title_id, topic_id):
       
        return self.sections[title_id][topic_id] 
    def reset(self):
        self.sections={}    
    
    
class Sections_Controller(Topics_Controller):  
    def __init__(self):
        Topics_Controller.__init__(self)
        self.section = Section()
        self.sections={}
        pub.subscribe(self.set_sections, "set_sections")

    def set_sections(self, title_id, topic_id):
        print(f"set_sections: Title ID: {title_id} topic_id {topic_id}")
        self.section.set_sections(title_id, topic_id)
        
        self.sections = self.section.get_sections(title_id, topic_id)
        #pp(self.topics)
        #print(f"topics: {self.topics}")
        pub.sendMessage("display_html")
        print(f"end of set_sections")

         
      

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
        print(f"BLOG: Navigating to: {url[:50]}")
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

            elif type == "show_topics":
                tid=int(tid)
                print(f"Title ID: {tid}")
                pub.sendMessage("set_topics", title_id=tid)  

            elif type == "show_sections":
                title_id,topic_id=tid.split("_")
                print(f"Title ID: {title_id}, Topic ID: {topic_id}")
                pub.sendMessage("set_sections", title_id=int(title_id), topic_id=int(topic_id))  

            elif type == "show_start":
                self.set_initial_content()                
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")


