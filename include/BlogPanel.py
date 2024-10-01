import wx
from pubsub import pub
from pprint import pprint as pp 
import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log
class Blog():
    def __init__(self):
        self.set_blog()

    def set_blog(self):
        self.blog = {'title': {'name':'','topics':[]} }

    def get_blog(self):
        return self.blog

    def reset(self):
        self.set_blog()
class Blog_Controller():  
    def __init__(self):
        self.blog = Blog()
        self.title_html=''
        self.topic_html=''
        pub.subscribe(self.use_title, "use_title")
        pub.subscribe(self.use_topic, "use_topic")
        pub.subscribe(self.reset_blog, "reset_blog")
    
    def reset_blog(self, tid):
        print(f"Resetting blog: {tid}")
        self.blog.reset()
        #self.set_titles()
    def use_title(self, tid):
        print(f"Using title: {tid}")
        blog = self.blog.get_blog()
        title= apc.titles[tid]
        blog['title']['name'] = title
        
        title_html= "<table>"
        #for sname, section in blog.items(): #<button onclick="testButtonClicked({sname})">del</button>
        title_html += f'''<tr><td></td><td><b>Title #{tid}</b><br><b style="font-size: 26px;">{title}</b></td></tr>
        '''
        title_html += "</table>"

        self.title_html=title_html
        self.show_html()
    
    def  use_topic(self, tid, toid):
        print(f"Using topic: {tid}, {toid}")
        topic= apc.topics[tid][toid]
        #print(777777, topic)
        
        blog = self.blog.get_blog()
        for top in blog['title']['topics']:
            top['active']=False
            if top['title']['tid'] == tid and top['toid']==toid:
                log('Topic is already used')
                return
        blog['title']['topics'].append({'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
        topic_html= self.get_topic_html(blog)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
    def get_topic_html(self, blog):
        topic_html= "<table>"
        for top in blog['title']['topics']: #<button onclick="testButtonClicked({sname})">del</button>
            top_id=top['toid'] 
            title_id=top['title']['tid'] 
            name=top['name']
            assert name
            title=top['title']['name']
            active=top['active']    
            active_btn = '<span style="color: #FF6666;">Active</span>'
            if not active:
                active_btn= f'<button id="activate-button"  onclick="activateTopic({title_id},{top_id})">Activate</button>'
            
            topic_html += f'<tr><td style="vertical-align: top;" >Topic<br>{top_id}<br>{active_btn}</td><td><b style="font-size: 20px;">{name}</b></td></tr><tr><td></td><td style="padding-left: 20px;">Title {title_id}: {title}</td></tr>'
            #add sections here 
            if active:
                topic_html += f'<tr><td colspan=2><span style="color: #FF6666;">New Topic goes here -- >>> </span></td></tr>'
        topic_html += "</table>"

        return topic_html        
    def  use_section(self, tid, toid, sid):
        print(f"Using topic: {tid}, {toid}, {sid}")
        topic= apc.topics[tid][toid]
        #print(777777, topic)
        
        blog = self.blog.get_blog()

        blog['title']['topics'].append({'name':topic,'sections':[],'title': apc.titles[tid]})
        
        topic_html= self.get_topic_html(blog)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()

    def show_html(self):
        
        new_html = """
        <html>
        <body>
    <head>
    
            <style>
               #activate-button { 
                   

                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #90EE90  ;
                    color: black;
                    border: none;
                    border-radius: 2px;
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
                <h1>Blog</h1>
                <a href="app:reset_blog:0">Reset</a>
            </div>
            %s
            %s
            <script>
                function testButtonClicked(tid) {
                    console.log('Test button clicked', tid);
                    window.location.href = 'app:titles:'+tid;
                }
            </script>
            <script>
                function activateTopic(tid, toid) {
                    console.log('activateTopic button clicked', tid, toid);
                    window.location.href = 'app:activate_topic:'+tid+'_' + toid;
                }
            </script>            
        </body>
        </html>
        """ % (self.title_html, self.topic_html)
        self.web_view.SetPage(new_html, "")

    def _set_titles(self):
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

    def activate_topic(self, tid, toid):
        print(f"activate_topic: {tid, toid}")
        blog = self.blog.get_blog()
        for top in blog['title']['topics']:
            top['active']=False
            if top['title']['tid'] == tid and top['toid']==toid:
                top['active']=True
        
        pp(blog)
        
        topic_html= self.get_topic_html(blog)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
class Blog_WebViewPanel(wx.Panel, Blog_Controller):
    def __init__(self, parent,):
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
        sizer.Add(self.web_view, 1, wx.EXPAND,0)
        self.SetSizer(sizer)
    def actiate_topic(self, tid, toid):
        print(f"activate_topic: {tid, toid}")
        self.activate_topic(tid, toid)

        


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
            <h1>Blog</h1>
            <div id="input-container">
                <textarea id="user-input" placeholder="Enter your title here">Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI</textarea>
                
            </div>
            <div id="button"><button id="start-button" onclick="startButtonClicked()">Set title</button></div>
            <br><br><br>
            <div id="output"></div>
            <script>
                function startButtonClicked() {
                    var userInput = document.getElementById('user-input').value;
                    document.getElementById('output').innerHTML = 'You entered: ' + userInput;
                    window.location.href = 'app:set_title:' + encodeURIComponent(userInput);
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
            if type == "set_title":
                title= self.decode(payload)
                print(f"Setting title: {title}")
            if type == "reset_blog":
                title= self.decode(payload)
                print(f"Resetting blog: {title}") 
                self.blog.reset() 
                self.set_initial_content()  
            if type == "activate_topic":
                tid, toid = payload.split("_")
                tid, toid = int(tid), int(toid)
                #title= self.decode(payload)
                print(f"activate_topic: {tid, toid}")
                self.actiate_topic(tid, toid)   
            
            event.Veto()  # Prevent actual navigation for our custom scheme

    def on_webview_error(self, event):
        print(f"WebView error: {event.GetString()}")



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
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)