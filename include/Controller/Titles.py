
import wx
import shutil, traceback
import os,sys,time, json
from os.path import join
from pubsub import pub
from datetime import date
from os.path import isfile, isdir
from pprint import pprint as pp 
class notImplementedError(Exception):
    pass


import include.config.init_config as init_config 
apc = init_config.apc
log=apc.log

def format_stacktrace():
    parts = ["Traceback (most recent call last):\n"]
    parts.extend(traceback.format_stack(limit=25))
    parts.extend(traceback.format_exception(*sys.exc_info())[1:])
    return "".join(parts)
class NotifyingDict(dict):
    def __init__(self, *args, parent=None, key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.key = key
        self._processing = False
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = NotifyingDict(v, parent=self, key=k)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NotifyingDict):
            value = NotifyingDict(value, parent=self, key=key)
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
            if isinstance(self.parent, NotifyingDict):
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



class Title():
    titles = MutableDictAttribute()
    def __init__(self):
        #self.titles = []
        self.init()
        assert apc.blog_name, 'Blog name not set'
        self.log_dir = log_dir=join('log', apc.blog_name)
        self.latest_dir=latest_dir=join(log_dir, 'latest')
        ts=apc.ts
        
        self.titles_fn=titles_fn=join(latest_dir, f'titles_{ts}.json')          
        if not isdir(latest_dir):
            os.makedirs(latest_dir)
 

        if 1:
            self.reset()
        
        if 0:
            if not self.titles:
                print('Setting titles--------------------------------')
                self.set_titles()
            else:
                print('Titles already set')
                print(self.titles)
                #e()
    def init(self):
        self.cfg={}
        self.mta=set()
        self.dump_file={}


    def set_titles(self):
        pp(self.titles)
        self.titles[apc.current_title]  ={}
        if apc.mock:
            for tid, tt in enumerate(["Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI",
            "Empowering the Next Generation: DeepLearning.AI's Role in AI Education and Workforce Development",
            "Leading the Way: Groundbreaking Research and Innovations from DeepLearning.AI",
            "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI",
            "Ethics in AI: DeepLearning.AI's Journey Towards Responsible and Fair Artificial Intelligence"]):
                #self.titles[title_set_name][str(tid)]=dict(title=tt)
                self.titles[apc.current_title][str(tid)]={}
                self.titles[apc.current_title][str(tid)]['title']=tt
                
            log('Mock Titles set')
            #self.titles[0]['title']='Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI'
        else:
            raise NotImplementedError
        apc.titles=self.titles[apc.current_title]

    def get_titles(self):
        return self.titles[apc.current_title]

    def process(self, attr_name, value):
        
        #print   ('-----Processing:', attr_name, value)
        if attr_name in self.mta: # ['page_id', 'reel_id', 'user_token','followers_count','uploaded_cnt']:
            #print(f"Parent processing: {attr_name} = {value}")
            if value is not None:
                self.set_attr(attr_name, value)
            return value
    def reset(self, hard=False):
        log_dir, latest_dir = self.log_dir, self.latest_dir
        assert isdir(latest_dir), latest_dir
        assert isdir(log_dir), log_dir
        files = os.listdir(latest_dir)
        files = [f for f in files if f.startswith('titles') and f.endswith('.json')]
        #pp(files)
        assert len(files) <= 1, ('Should be only one latest file', files)
        if files:
            assert isfile(join(latest_dir, files[0])), ('Should be a file', files[0])
            shutil.copy(join(latest_dir, files[0]), join(log_dir, files[0]))
            os.rename(join(latest_dir, files[0]), self.titles_fn)
            if hard:
                os.remove(self.titles_fn)
                assert not isfile(self.titles_fn), self.titles_fn
                self.titles_fn=join(latest_dir, f'titles_{apc.ts}_reset.json')
                self.init()
                       
        self.titles=self.get_attr('titles', {apc.current_title:{}}, self.titles_fn)
        apc.titles=self.titles[apc.current_title]


    
    def get_attr(self, attr, default=None, dump_file='.config.json'): 
        
        if attr not in self.dump_file:
            self.dump_file[attr]=dump_file
        config_fn=self.dump_file[attr]
        self.mta.add(attr)
        print('-------------------config_fn: ' , attr, config_fn)
        if config_fn not in self.cfg:
            self.cfg[config_fn]={}
        cfg=self.cfg[config_fn]

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
                            self.cfg[config_fn]=cfg=cfg_dump
                        else:
                            print(f"Warning: {config_fn} is empty.")
                except json.JSONDecodeError as e:
                    print(f"Error reading config file {config_fn}: {e}")
                    #print("Initializing with an empty PropertyDefaultDict.")
                except Exception as e:
                    print(f"Unexpected error reading config file {config_fn}: {e}")
                    #print("Initializing with an empty PropertyDefaultDict.")
            else:
                print(f"Warning: connfig file {config_fn} does not exist.")
            
                
        if cfg:
            print(8888, cfg)
            #print (attr.name)
            value=cfg.get(attr, default)
            print('Getting:', attr, type(value))   
           
            
            return value
        self.cfg[config_fn]=cfg
        print('returning ',attr,  default)

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
        print('Dumping ******************************:', attr, dump_file)    
     
        with open(dump_file, 'w') as f:
            json.dump(cfg, f, indent=2)        
    
class Titles_Controller():  
    def __init__(self):
        self.title = Title()
        #self.titles=self.title.get_titles()
        pub.subscribe(self.set_titles, "set_titles")
        pub.subscribe(self.display_html, "display_html")
        print('Titles_Controller: __init__')

    def set_titles(self, user_input):
        self.title.set_titles()
        self.titles = self.title.get_titles()
        
        apc.prompt=user_input
        #print(f"Titles: {self.titles}")
        self.display_html()
    def display_html(self):
        self.titles = self.title.get_titles()
        #print("Titles_Controller: display_html")
        titles_html= """<button id="titles-button"  onclick="showTitles({tid},{toid})" style="position: absolute; left: 0;">Titles</button>
<table>"""

        #pp(self.titles)
        
        for tid, titled in self.titles.items():
            #tid=str(tid)
            
            title=titled['title']
            print   (f"display_html: Title: {tid}. {title}")
            topics = self.topic.get_topics(tid)
            if topics:
                #print(f"display_html: topic.topics: {tid}")
                #exit(   )
                
                topics_html ="<table>"

               
                for toid, topicd in topics.items():
                    toid=str(toid)
                    #print(f"display_html: Title: {tid} Topic: {toid}. {topic}")  
                    sections=self.section.get_sections(tid, toid)
                    if sections:
                        section_html = "<table>"
                        
                        print(f"tid in section: {tid}")
                        if 1:
                            print(f"toid in section.sections: {toid}")
                            for sid, sectiond in sections.items():
                                section = sectiond['section']   
                                section_html += f'''<tr><td><td class="td-cell"><button id="use-button"  onclick="useSection({tid},{toid},{sid})"><<<</button></td>
                                <td><span class="blue-border">{section}</span>
                                <br>
                                
                                </td></tr>'''
                        section_html +="</table>"
                    else:
                        section_html = "No sections"
                    topic_border='black_border'
                    print(f"---------------------------------expanded_topic: {apc.expanded_topic} toid: {toid}")
                    if apc.expanded_title == tid and apc.expanded_topic == toid:
                        topic_border='fancy-border'
                    topic = topicd['topic']
                    topics_html += f'''<tr><td class="td-cell"><button id="use-button"  onclick="useTopic({tid},{toid})"><<<</button></td>
                    <td> </td><td><a id="topic_{tid}_{toid}"></a><span class="{topic_border}">{topic}</span>
                    <br>
                    <button id="sections-button"  onclick="sectionsButtonClicked({tid},{toid})">sections</button> <br>
                    {section_html}
                    </td></tr>''' 
                
                topics_html +="</table>"
            else:
                #pp(self.topic.topics)
                #e()
                topics_html = str(self.topic.topics.keys()) + f'No topics for {tid}.'+str(type(tid))+'.' + str(tid in self.topic.topics) + str(self.title.titles)
            title_border='black_border'
            if apc.expanded_title == tid:
                title_border='fancy-border'
            titles_html += f'''<tr><td ><button id="yel-button"  onclick="useTitle({tid})"><<<</button></td>
            <td><a id="title_{tid}"></a><span class="{title_border}">{title}</span></tr>
            <tr><td></td><td > <button id="topics-button"  onclick="topicsButtonClicked({tid})">topics</button> <br>
            {topics_html}
            </td></tr>'''
        titles_html += "</table>"

        new_html = """
        <html>
       <head>
           <style>

                .td-cell {
                    position: relative; /* Make td the reference for the button positioning */
                    }

    

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
                #titles-button { 
                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #3C3C3C ;
                    color: white;
                    border: none;
                    border-radius: 2px;
                }                
                #topics-button { 
                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: gray ;
                    color: white;
                    border: none;
                    border-radius: 2px;
                }
                #sections-button { 
                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #A9A9A9 ;
                    color: white;
                    border: none;
                    border-radius: 2px;
                }                
                #start-button:hover {
                    background-color: #45a049;
                }
                #use-button { 
                    position: absolute;
                    top: 0;    /* Adjust to position it on top */
                    left: 55%%; /* Center horizontally if desired */
                    

                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #FFFFE0  ;
                    color: black;
                    border: none;
                    border-radius: 2px;
                }
                #use-button:hover {
                    background-color: #45a049;
                } 
                #yel-button { 
            

                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: #FFFFE0  ;
                    color: black;
                    border: none;
                    border-radius: 2px;
                }
                #yel-button:hover {
                    background-color: #45a049;
                } 
                #preview-button { 
                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: green ;
                    color: white;
                    border: none;
                    border-radius: 2px;
                }
                #preview-button:hover {
                    background-color: #45a049;
                }                               
                #reset-button { 
                    padding: 2px 5px;
                    font-size: 16px;
                    cursor: pointer;
                    background-color: red ;
                    color: white;
                    border: none;
                    border-radius: 2px;
                }
                #reset-button:hover {
                    background-color: #45a049;
                }  
                .black_border {
                    display: inline-block;
                    padding: 10px;
                    border: 1px solid black;  /* Thin black border */
                    border-radius: 5px;       /* Rounded corners */
                    font-weight: bold;
                    margin: 10px 0;
                }  
                .purple-border {
                    display: inline-block;
                    padding: 10px;
                    border: 1px solid purple;  /* Thin black border */
                    border-radius: 5px;       /* Rounded corners */
                    font-weight: bold;
                    margin: 10px 0;
                }    
                .blue-border {
                    display: inline-block;
                    padding: 10px;
                    border: 1px solid blue;  /* Thin black border */
                    border-radius: 5px;       /* Rounded corners */
                    font-weight: bold;
                    margin: 10px 0;
                }                                             
                .fancy-border {
                    display: inline-block;
                    padding: 10px;
                    border: 4px solid transparent;
                    border-image: linear-gradient(to bottom right, #b827fc 0%%, #2c90fc 25%%, #b8fd33 50%%, #fec837 75%%, #fd1892 100%%);
                    border-image-slice: 1;
                    font-weight: bold;
                    margin: 10px 0;
                }                                              
            </style>
        </head>        
        <body>
            <pre>
                <div id="header-container">
                <h1>%s</h1>
                 <button id="preview-button"  onclick="previewButtonClicked()">Preview</button>
               <button id="reset-button"  onclick="resetButtonClicked()">Reset</button>
            </div>
            %s
            
            
            
            </pre>
            <script>
                function useTitle(tid) {
                    console.log('Test button clicked', tid);
                    window.location.href = 'app:use_title:'+tid;
                }
                function topicsButtonClicked(tid, toid) {
                    console.log('topics button clicked', tid);
                    window.location.href = 'app:show_topics:'+tid;
                }    
                function resetButtonClicked() {
                    console.log('reset button clicked');
                    window.location.href = 'app:reset_titles:0';
                }  
                function previewButtonClicked() {
                    console.log('preview button clicked');
                    window.location.href = 'app:preview:0';
                }                 
                function sectionsButtonClicked(tid, toid) {
                    console.log('sections button clicked');
                    window.location.href = 'app:show_sections:'+tid+'_'   +toid;
                }     
                function useSection(tid, toid, sid) {
                    console.log('useSection button clicked');
                    window.location.href = 'app:use_section:'+tid+'_'   +toid+'_' +sid;
                }  
                function useTopic(tid, toid) {
                    console.log('useTopic button clicked');
                    window.location.href = 'app:use_topic:'+tid+'_'   +toid;
                }                                                                     
            </script>
        </body>
        </html>
        """ % (apc.prompt, titles_html)
        self.web_view.SetPage(new_html, "")  