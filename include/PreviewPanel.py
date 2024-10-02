import wx
from pubsub import pub
from pprint import pprint as pp 
import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log
apc.used_section=None
apc.used_section    =None
class Preview():
    def __init__(self):
        self.set_blog()

    def set_blog(self):
        self.blog = {'title': {'name':'','topics':[]} }

    def get_blog(self):
        return self.blog

    def reset(self):
        self.set_blog()
class Preview_Controller():  
    def __init__(self):
        self.blog = Preview()
        self.title_html=''
        self.topic_html=''
        pub.subscribe(self.use_title, "use_title")
        pub.subscribe(self.use_topic, "use_topic")
        pub.subscribe(self.use_section, "use_section")
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
        #title_html += f'''<tr><td></td><td><b>Title #{tid}</b><br><b style="font-size: 26px;">{title}</b></td></tr>'''
        title_html += f'''<tr><td></td><td><br><b style="font-size: 26px;">{title}</b></td></tr>'''
        title_html += "</table>"

        self.title_html=title_html
        self.show_html()
    
    def  use_topic(self, tid, toid):
        print(f"Using topic: {tid}, {toid}")
        topic= apc.topics[tid][toid]
        #print(777777, topic)
        
        blog = self.blog.get_blog()
        active_tid=None
        for ttid, top in enumerate(blog['title']['topics']):
            if top['title']['tid'] == tid and top['toid']==toid:
                log('Topic is already used')
                return            
            if top['active']:
                active_tid=ttid
                
            top['active']=False
            #deactivate sections
            for sec in top['sections']:
                sec['active']=False
        if active_tid is not None:
                blog['title']['topics'].insert(active_tid+1, {'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
                apc.used_topic=active_tid+1
        else:
            blog['title']['topics'].append({'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
            apc.used_topic=len(blog['title']['topics'])-1
        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', apc.used_topic)
        topic_html= self.get_topic_html(blog)

        

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
        self.web_view.RunScriptAsync(f"window.location.href = '#topic_{tid}_{toid}';")
    def get_topic_html(self, blog):
        topic_html= "<table>"
        for ttoid, top in enumerate(blog['title']['topics']): #<button onclick="testButtonClicked({sname})">del</button>
            top_id=top['toid'] 
            title_id=top['title']['tid'] 
            name=top['name']
            assert name
            title=top['title']['name']
            active=top['active']    
            active_btn = '<span style="color: #FF6666;">Active</span>'
            if not active:
                active_btn= f'<button id="activate-button"  onclick="activateTopic({title_id},{top_id})">Activate</button>'
            topic_border='topic-border'
            if apc.used_topic == ttoid:
                topic_border='fancy-border'
            #print('//////////////////////////////////////////////////', top_id, apc.used_topic, topic_border)
            if 0:
                topic_html += f'''<tr><td style="vertical-align: top;" >Topic<br>{top_id}<br>{active_btn} <a id="topic_{title_id}_{top_id}"></a></td>
            <td><span class="{topic_border}"><b style="font-size: 20px;">{name}</b></span></td></tr>
            <tr><td></td><td style="padding-left: 20px;">Title {title_id}: {title}</td></tr>'''
            else:
                topic_html += f'''<tr><td style="vertical-align: top;" ><a id="topic_{title_id}_{top_id}"></a></td>
            <td><b style="font-size: 20px;">{name}</b></td></tr>
            '''                
            #add sections here 
            section_html='<table>'
            for ssid,sec in enumerate(top['sections']):
                sec_id=sec['sid']
                sec_name=sec['name']
                sec_active=sec['active']
                sec_title_id=sec['title']['tid']
                sec_title=sec['title']['name']
                sec_topic_id=sec['topic']['toid']
                sec_topic=sec['topic']['name']
                sec_active_btn = '<span style="color: #FF6666;">Active</span><br><span style="color: #FF6666;">New Section goes here -- >>> </span>'
                if not sec_active:
                    sec_active_btn= f'<button id="activate-button"  onclick="activateSection({title_id},{top_id},{sec_id})">Activate</button>'
                sec_border='section-border'
                if apc.used_section == ssid:
                    sec_border='fancy-border'              
                    
                #section_html += f'<tr><td></td><td ><span class="{topic_border}"> Section {sec_id}: <b style="font-size: 16px;">{sec_name} </b></span>{sec_active_btn}</td></tr>'
                section_html += f'<tr><td></td><td > <span style="font-size: 16px;">{sec_name} </span></td></tr>'
                #section_html += f'<tr><td></td><td style="padding-left: 10px;">Title {sec_title_id}: {sec_title}</td></tr>'
                #section_html += f'<tr><td></td><td style="padding-left: 10px;">{sec_title}</td></tr>'
                #section_html += f'<tr><td></td><td style="padding-left: 20px;">Topic {sec_topic_id}: {sec_topic}</td></tr>'
                #section_html += f'<tr><td></td><td style="padding-left: 20px;">{sec_topic}</td></tr>'
            section_html += '</table>'

            topic_html +=  f'<tr><td></td><td>{section_html}</td></tr>'
            if 0 and active:
                topic_html += f'<tr><td colspan=2><span style="color: #FF6666;">New Topic goes here -- >>> </span></td></tr>'
        topic_html += "</table>"

        return topic_html        
    def  use_section(self, tid, toid, sid):
        print(f"Using section: {tid}, {toid}, {sid}")
        if 1:
            topic= apc.topics[tid][toid]
            #print(777777, topic)
            section= apc.sections[tid][toid][sid]
            blog = self.blog.get_blog()
            #get active blog topic
            if not blog['title']['topics']:
                log('Cannot add section without topic','error')
            for top in blog['title']['topics']:
                if top['active']:
                    #deactivate all sections
                    active_sid=None
                    for sec in top['sections']:
                        if sec['active']:
                            active_sid=sec['sid']
                        sec['active']=False
                    
                    if active_sid is not None:
                        top['sections'].insert(active_sid+1, {'sid':sid,'name':section, 'active':True, 'title': {'tid':tid,'name':apc.titles[tid]}, 'topic': {'toid':toid,'name':topic}})
                        apc.used_section=active_sid+1
                    else:
                        top['sections'].append({'sid':sid,'name':section, 'active':True, 'title': {'tid':tid,'name':apc.titles[tid]}, 'topic': {'toid':toid,'name':topic}})  
                        apc.used_section=len(top['sections'])-1
            #blog['title']['topics'].append({'name':topic,'sections':[],'title': apc.titles[tid]})
            
            topic_html= self.get_topic_html(blog)

            #print(999, topic_html)
            self.topic_html=topic_html
            pp(blog['title']['topics'])
        self.show_html()

    def show_html(self):
        
        new_html = """
        <html>
        <body>
    <head>
    
            <style>

                .fancy-border {
                    display: inline-block;
                    padding: 10px;
                    border: 4px solid transparent;
                    border-image: linear-gradient(to bottom right, #b827fc 0%%, #2c90fc 25%%, #b8fd33 50%%, #fec837 75%%, #fd1892 100%%);
                    border-image-slice: 1;
                    font-weight: bold;
                    margin: 10px 0;
                }
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
                <a href="app:show_explore:0">Explore</a>
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
            <script>
                function activateSection(tid, toid, sid) {
                    console.log('activateSection button clicked', tid, toid, sid);
                    window.location.href = 'app:activate_section:'+tid+'_' + toid + '_' + sid;
                }
            </script>                     
        </body>
        </html>
        """ % (self.title_html, self.topic_html)
        self.web_view.SetPage(new_html, "")

   

    def activate_topic(self, tid, toid):
        print(f"activate_topic: {tid, toid}")
        blog = self.blog.get_blog()
        for ttoid, top in enumerate(blog['title']['topics']):
            top['active']=False
            #deactivate sections too
            for sec in top['sections']:
                sec['active']=False
            if top['title']['tid'] == tid and top['toid']==toid:
                top['active']=True
                apc.used_topic=ttoid
                #activate last section
                if top['sections']:
                    top['sections'][-1]['active']=True
                    apc.used_section=len(top['sections'])-1
        
        pp(blog)
        
        topic_html= self.get_topic_html(blog)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
    def activate_section(self, tid, toid, sid):
        print(f"activate_section: {tid, toid}")
        blog = self.blog.get_blog()
        for top in blog['title']['topics']:
            top['active']=False
            if top['title']['tid'] == tid and top['toid']==toid:
                top['active']=True
                for sec in top['sections']:
                    sec['active']=False
                    if sec['sid'] == sid:
                        sec['active']=True
        
        pp(blog)
        
        topic_html= self.get_topic_html(blog)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()        
class Preview_WebViewPanel(wx.Panel, Preview_Controller):
    def __init__(self, parent,):
        super().__init__(parent)
        Preview_Controller.__init__(self)
        
        # Create the WebView control
        self.web_view = wx.html2.WebView.New(self)
        
        # Attach custom scheme handler
        #self.attach_custom_scheme_handler()

        # Bind navigation and error events
        self.web_view.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.on_navigation_request)
        #self.web_view.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.on_webview_error)

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
                <h1>Blog</h1>
                <div id="button">Start with <button id="activate-button" onclick="startButtonClicked()">Exploration</button></div>
                <div id="output"></div>
                <script>
                    function startButtonClicked() {
                        console.log('Start button clicked');
                        window.location.href = 'app:show_explore';  // Trigger the navigation event
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
    def on_navigation_request(self, event):
        url = event.GetURL()
        
        # Check if the custom scheme 'app:' is used
        if url.startswith("app:show_explore"):
            event.Veto()  # Stop the browser from navigating away
            pub.sendMessage("show_explore_tab")
            # Add your Python logic here
        else:
            event.Skip()  # Allow normal navigation for other URLs

    def on_navigating(self, event):
        url = event.GetURL()
        print(f"Blog Navigating to: {url[:50]}")
        if url.startswith("app:"):
            _, type,payload = url.split(":")
            if type == "show_explore":
                #title= self.decode(payload)
                print(f"Sending to Explore")
                pub.sendMessage("show_explore_tab")
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



class PreviewPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        panel = self #wx.Panel(self)
        # Create a notebook control
        self.notebook = wx.Notebook(panel)

        # Create an instance of WebViewPanel
        self.web_view_panel = Preview_WebViewPanel(self.notebook)

        # Add the WebViewPanel to the notebook with the label "Titles"
        self.notebook.AddPage(self.web_view_panel, "Blog")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)