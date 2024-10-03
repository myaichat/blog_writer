
import wx
import os, sys, json, shutil
from  os.path import isfile, isdir, join
from pubsub import pub
from pprint import pprint as pp 

import include.config.init_config as init_config 
apc = init_config.apc
log=apc.log
class notImplementedError(Exception):
    pass

class Design():
    def __init__(self):
        self.set_design()

    def set_design(self):
        self.design = {'title': {'name':'','topics':[]} }

    def get_design(self):
        return self.design

    def reset(self):
        self.set_design()
class Design_Controller():  
    def __init__(self):
        self.design = Design()
        self.title_html=''
        self.topic_html=''
        pub.subscribe(self.use_title, "use_title")
        pub.subscribe(self.use_topic, "use_topic")
        pub.subscribe(self.use_section, "use_section")
        pub.subscribe(self.reset_design, "reset_design")
    
    def reset_design(self, tid):
        print(f"Resetting design: {tid}")
        self.design.reset()
        #self.set_titles()
    def use_title(self, tid):
        print(f"Using title: {tid}")
        design = self.design.get_design()
        title= apc.titles[tid]['title']
        design['title']['name'] = title
        
        title_html= "<table>"
        #for sname, section in design.items(): #<button onclick="testButtonClicked({sname})">del</button>
        title_html += f'''<tr><td></td><td><b>Title #{tid}</b><br><b style="font-size: 26px;">{title}</b></td></tr>
        '''
        title_html += "</table>"

        self.title_html=title_html
        self.show_html()
    
    def  use_topic(self, tid, toid):
        print(f"Using topic: {tid}, {toid}")
        topic= apc.topics[tid][toid]
        #print(777777, topic)
        
        design = self.design.get_design()
        active_tid=None
        for ttid, top in enumerate(design['title']['topics']):
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
                design['title']['topics'].insert(active_tid+1, {'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
                apc.used_topic=active_tid+1
        else:
            design['title']['topics'].append({'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
            apc.used_topic=len(design['title']['topics'])-1
        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', apc.used_topic)
        topic_html= self.get_topic_html(design)

        

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
        self.web_view.RunScriptAsync(f"window.location.href = '#topic_{tid}_{toid}';")
    def get_topic_html(self, design):
        topic_html= "<table>"
        for ttoid, top in enumerate(design['title']['topics']): #<button onclick="testButtonClicked({sname})">del</button>
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
            topic_html += f'''<tr><td style="vertical-align: top;" >Topic<br>{top_id}<br>{active_btn} <a id="topic_{title_id}_{top_id}"></a></td>
            <td><span class="{topic_border}"><b style="font-size: 20px;">{name}</b></span></td></tr>
            <tr><td></td><td style="padding-left: 20px;">Title {title_id}: {title}</td></tr>'''
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
                    
                section_html += f'<tr><td></td><td ><span class="{topic_border}"> Section {sec_id}: <b style="font-size: 16px;">{sec_name} </b></span>{sec_active_btn}</td></tr>'
                section_html += f'<tr><td></td><td style="padding-left: 10px;">Title {sec_title_id}: {sec_title}</td></tr>'
                section_html += f'<tr><td></td><td style="padding-left: 20px;">Topic {sec_topic_id}: {sec_topic}</td></tr>'
            section_html += '</table>'

            topic_html +=  f'<tr><td></td><td>{section_html}</td></tr>'
            if active:
                topic_html += f'<tr><td colspan=2><span style="color: #FF6666;">New Topic goes here -- >>> </span></td></tr>'
        topic_html += "</table>"

        return topic_html        
    def  use_section(self, tid, toid, sid):
        print(f"Using section: {tid}, {toid}, {sid}")
        if 1:
            topic= apc.topics[tid][toid]
            #print(777777, topic)
            section= apc.sections[tid][toid][sid]
            design = self.design.get_design()
            #get active design topic
            if not design['title']['topics']:
                log('Cannot add section without topic','error')
            for top in design['title']['topics']:
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
            #design['title']['topics'].append({'name':topic,'sections':[],'title': apc.titles[tid]})
            
            topic_html= self.get_topic_html(design)

            #print(999, topic_html)
            self.topic_html=topic_html
            pp(design['title']['topics'])
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
                <h1>Design</h1><a href="app:show_preview:0">Preview</a>
                <a href="app:reset_design:0">Reset</a>
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
        design = self.design.get_design()
        for ttoid, top in enumerate(design['title']['topics']):
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
        
        pp(design)
        
        topic_html= self.get_topic_html(design)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
    def activate_section(self, tid, toid, sid):
        print(f"activate_section: {tid, toid}")
        design = self.design.get_design()
        for top in design['title']['topics']:
            top['active']=False
            if top['title']['tid'] == tid and top['toid']==toid:
                top['active']=True
                for sec in top['sections']:
                    sec['active']=False
                    if sec['sid'] == sid:
                        sec['active']=True
        
        pp(design)
        
        topic_html= self.get_topic_html(design)

        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()        
