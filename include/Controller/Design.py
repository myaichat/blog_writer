
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
class NotifyingDict(dict):
    def __init__(self, *args, parent=None, key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.key = key
        self._processing = False
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = NotifyingDict(v, parent=self, key=k)
            elif isinstance(v, list):
                self[k] = NotifyingList(v, parent=self, key=k)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NotifyingDict):
            value = NotifyingDict(value, parent=self, key=key)
        elif isinstance(value, list) and not isinstance(value, NotifyingList):
            value = NotifyingList(value, parent=self, key=key)
        super().__setitem__(key, value)
        self.propagate_change()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'NotifyingDict' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ['parent', 'key', '_processing']:
            super().__setattr__(name, value)
        else:
            self[name] = value

    def propagate_change(self):
        if self.parent and not self._processing:
            if isinstance(self.parent, (NotifyingDict, NotifyingList)):
                self.parent.propagate_change()
            elif isinstance(self.parent, MutableDictAttribute):
                self.parent.child_changed()

class NotifyingList(list):
    def __init__(self, *args, parent=None, key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.key = key
        self._processing = False
        for i, v in enumerate(self):
            if isinstance(v, dict):
                self[i] = NotifyingDict(v, parent=self, key=i)
            elif isinstance(v, list):
                self[i] = NotifyingList(v, parent=self, key=i)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NotifyingDict):
            value = NotifyingDict(value, parent=self, key=key)
        elif isinstance(value, list) and not isinstance(value, NotifyingList):
            value = NotifyingList(value, parent=self, key=key)
        super().__setitem__(key, value)
        self.propagate_change()

    def append(self, value):
        if isinstance(value, dict) and not isinstance(value, NotifyingDict):
            value = NotifyingDict(value, parent=self, key=len(self))
        elif isinstance(value, list) and not isinstance(value, NotifyingList):
            value = NotifyingList(value, parent=self, key=len(self))
        super().append(value)
        self.propagate_change()

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def propagate_change(self):
        if self.parent and not self._processing:
            if isinstance(self.parent, (NotifyingDict, NotifyingList)):
                self.parent.propagate_change()
            elif isinstance(self.parent, MutableDictAttribute):
                self.parent.child_changed()

class MutableDictAttribute:
    def __init__(self):
        self.parent = None
        self.name = None
        self.real_name = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"
        self.real_name = name

    def __get__(self, obj, objtype=None):
        if self.parent is None:
            self.parent = obj
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        if isinstance(processed_value, dict):
            processed_value = NotifyingDict(processed_value, parent=self, key=self.real_name)
        elif isinstance(processed_value, list):
            processed_value = NotifyingList(processed_value, parent=self, key=self.real_name)
        setattr(obj, self.name, processed_value)

    def process(self, value):
        print('222 Processing:', self.real_name, value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def child_changed(self):
        if hasattr(self.parent, 'process'):
            current_value = getattr(self.parent, self.name, None)
            if current_value is not None:
                current_value._processing = True
                processed = self.parent.process(self.real_name, current_value)
                current_value._processing = False
                setattr(self.parent, self.name, processed)
class Design():
    designs=MutableDictAttribute()
    def __init__(self):
        self.init()
        assert apc.blog_name, 'Blog name not set'
        self.log_dir = log_dir=join('log', apc.blog_name)
        self.latest_dir=latest_dir=join(log_dir, 'latest')
        ts=apc.ts
        
        self.designs_fn=designs_fn=join(latest_dir, f'designs_{ts}.json')          
        if not isdir(latest_dir):
            os.makedirs(latest_dir)        
        self.reset()
    def init(self):
        self.cfg={}
        self.mta=set()
        self.dump_file={}
    def set_design(self):
        self.designs[apc.current_title]={}
        self.designs[apc.current_title]['title']={'name':'','topics':[]} 
        pass

    def get_design(self):
        return self.designs[apc.current_title]
    def get_name(self):
        return self.designs[apc.current_title]['title']['name']   

    def _reset(self):
        self.set_design()

    def process(self, attr_name, value):
        #print   ('-----Processing:', attr_name, value)
        if attr_name in self.mta: # ['page_id', 'reel_id', 'user_token','followers_count','uploaded_cnt']:
            #print(f"Parent processing: {attr_name} = {value}")
            if value:
                self.set_attr(attr_name, value)
            return value
    def reset(self, hard=False):
        log_dir, latest_dir = self.log_dir, self.latest_dir
        assert isdir(latest_dir), latest_dir
        assert isdir(log_dir), log_dir
        files = os.listdir(latest_dir)
        files = [f for f in files if f.startswith('designs') and f.endswith('.json')]
        pp(files)
        assert len(files) <= 1, ('Should be only one latest file', files)
        if files:
            assert isfile(join(latest_dir, files[0])), ('Should be a file', files[0])
            shutil.copy(join(latest_dir, files[0]), join(log_dir, files[0]))
            os.rename(join(latest_dir, files[0]), self.designs_fn)
            if hard:
                os.remove(self.designs_fn)
                assert not isfile(self.designs_fn), self.designs_fn
                self.designs_fn=join(latest_dir, f'designs_{apc.ts}_reset.json')
                self.init()

                       
        self.designs=self.get_attr('designs', {apc.current_title:{'title':{'name':'','topics':[]}}}, self.designs_fn)
        apc.designs=self.designs[apc.current_title]
        pp(self.designs)


    
    def get_attr(self, attr, default=None, dump_file='.config.json'): 
        if attr not in self.dump_file:
            self.dump_file[attr]=dump_file
        config_fn=self.dump_file[attr]
        self.mta.add(attr)
        #print('-------------------config_fn: ' , attr, config_fn)
        if config_fn not in self.cfg:
            self.cfg[config_fn]={}
        cfg=self.cfg[config_fn]
        #pp(cfg)
        if not cfg:
            if isfile(config_fn):
                try:
                    print(f"Reading config file {config_fn}")
                    with open(config_fn, 'r') as f:
                        content = f.read().strip()
                        #pp(content)
                        if content:
                            cfg_dump = json.loads(content)
                            #pp(cfg_dump)
                            #data=cfg=cfg_dump
                            if 1:
                                self.cfg[config_fn]=cfg=cfg_dump
                                #self.cfg[config_fn]['topics']={int(k):v for k,v in data['topics'].items()}
                                #cfg=self.cfg[config_fn]
                        else:
                            print(f"Warning: {config_fn} is empty.")
                except json.JSONDecodeError as e:
                    print(f"Error reading config file {config_fn}: {e}")
                    raise
                    #print("Initializing with an empty PropertyDefaultDict.")
                except Exception as e:
                    print(f"Unexpected error reading config file {config_fn}: {e}")
                    raise
                    #print("Initializing with an empty PropertyDefaultDict.")
            else:
                print(f"Warning: connfig file {config_fn} does not exist.")
            
                
        if cfg:
            #print(8888, cfg)
            #print (attr.name)
            value=cfg.get(attr, default)
            print('Getting:', attr, type(value))   
           
            
            return value
        self.cfg[config_fn]=cfg
        return default
    def set_attr(self, attr, value):
        #print('Setting:', attr, value, type(value))
        assert attr in self.dump_file, f'set_attr: No dump file specified for attr "{attr}"'
        dump_file = self.dump_file[attr]   
        assert dump_file, f'set_attr: dump_file is not set  for attr "{attr}"'     
        cfg=self.cfg[dump_file]
        #pp(self.cfg)
        assert cfg is not None, dump_file
        cfg[attr]=value

        assert dump_file, 'set_attr: No dump file specified'
        #pp(attr)
        #pp(value)
        print('Dumping ******************************:', attr, dump_file)    
        with open(dump_file, 'w') as f:
            json.dump(cfg, f, indent=2)

class Design_Controller():  
    def __init__(self):
        self.design = Design()
        self.title_html=''
        self.topic_html=''
        pub.subscribe(self.use_title, "use_title")
        pub.subscribe(self.use_topic, "use_topic")
        pub.subscribe(self.use_section, "use_section")
        #pub.subscribe(self.reset_design, "reset_design")
    
    def _reset_design(self, tid):
        print(f"Resetting designs: {tid}")
        #self.show_initial_content(hard_reset=True)
        self.design.reset()
        #self.set_titles()
    def get_title_html(self):
        design = self.design.get_design()
        pp(design)
        title= design['title']['name']
        #print(999, title)
        tid= design['title']['tid']
   
        title_list= list(self.design.designs.keys())
        title_html= "<table>"
        #for sname, section in design.items(): #<button onclick="testButtonClicked({sname})">del</button>
        title_html += f'''<tr><td></td><td><b>Title #{tid}</b>  {title_list}<br><b style="font-size: 26px;">{title}</b></td></tr>
        '''
        title_html += "</table>"
        return title_html
    def use_title(self, tid):
        print(f"Using title: {tid}")
        design = self.design.get_design()
        title= apc.titles[tid]['title']
        design['title']['name'] = title
        design['title']['tid'] = tid    
        title_list= list(self.design.designs.keys())
        title_html= "<table>"
        #for sname, section in design.items(): #<button onclick="testButtonClicked({sname})">del</button>
        title_html += f'''<tr><td></td><td><b>Title #{tid}</b> {title_list}<br><b style="font-size: 26px;">{title}</b></td></tr>
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
                design['title']['used_topic']=active_tid+1
        else:
            design['title']['topics'].append({'toid':toid,'name':topic,'active':True, 'sections':[],'title': {'tid':tid,'name':apc.titles[tid]}})
            design['title']['used_topic']=len(design['title']['topics'])-1
        #print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', apc.used_topic)
        design['title']['test']=1
        topic_html= self.get_topic_html()
        print('#'*80)
        pp(design)
        print('#'*80)
        #print(999, topic_html)
        self.topic_html=topic_html
        self.show_html()
        self.web_view.RunScriptAsync(f"window.location.href = '#topic_{tid}_{toid}';")
    def get_topic_html(self):
        design = self.design.get_design()
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
            if design['title']['used_topic'] == ttoid:
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
            
            topic_html= self.get_topic_html()

            #print(999, topic_html)
            self.topic_html=topic_html
            #pp(design['title']['topics'])
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
                <a href="app:reset_designs:0">Reset</a>
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
                design['title']['used_topic']=ttoid
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
