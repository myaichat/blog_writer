
import wx
import shutil
import os,sys,time, json
from os.path import join
from pubsub import pub
from datetime import date
from os.path import isfile, isdir
from pprint import pprint as pp 
class notImplementedError(Exception):
    pass

import include.config.init_config as init_config 
class MutableList(list):
    def __init__(self, parent_obj, descriptor):
        super().__init__(getattr(parent_obj, descriptor.name))
        self.parent_obj = parent_obj
        self.descriptor = descriptor

    def add_item(self, item):
        if not isinstance(item, dict):
            raise ValueError("Item must be a dictionary")
        self.append(item)
        self.descriptor.__set__(self.parent_obj, self)

    def remove_item(self, index):
        if 0 <= index < len(self):
            del self[index]
            self.descriptor.__set__(self.parent_obj, self)
        else:
            raise IndexError("Index out of range")

    def update_item(self, index, new_item):
        if not isinstance(new_item, dict):
            raise ValueError("New item must be a dictionary")
        if 0 <= index < len(self):
            self[index] = new_item
            self.descriptor.__set__(self.parent_obj, self)
        else:
            raise IndexError("Index out of range")
class MutableListAttribute:
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
        if not hasattr(obj, self.name):
            setattr(obj, self.name, [])
        return MutableList(obj, self)

    def __set__(self, obj, value):
        
        if not isinstance(value, list):
            raise ValueError("Value must be a list")
        if not all(isinstance(item, dict) for item in value):
            raise ValueError("All items in the list must be dictionaries")
        if self.parent is None:
            self.parent = obj
        processed_value = self.process(value)
        print('processed_value|__set__:',processed_value)
        
        setattr(obj, self.name, processed_value)
        self.notify_change(processed_value)

    def process(self, value):
        #print(f'Processing: {self.real_name}', value)
        if hasattr(self.parent, 'process'):
            return self.parent.process(self.real_name, value)
        return value

    def notify_change(self, value):
        pub.sendMessage(f'{self.real_name}_changed', value=value)



apc = init_config.apc
log=apc.log
class Title():
    titles = MutableListAttribute()
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
 

        else:
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
        
        if apc.mock:
            for tt in ["Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI",
            "Empowering the Next Generation: DeepLearning.AI's Role in AI Education and Workforce Development",
            "Leading the Way: Groundbreaking Research and Innovations from DeepLearning.AI",
            "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI",
            "Ethics in AI: DeepLearning.AI's Journey Towards Responsible and Fair Artificial Intelligence"]:
                self.titles.add_item(dict(title=tt))
            log('Mock Titles set')
            self.titles[0]['title']='Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI'
        else:
            raise NotImplementedError
        apc.titles=self.titles

    def get_titles(self):
        return self.titles

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
        pp(files)
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
                       
        self.titles=self.get_attr('titles', [], self.titles_fn)
        apc.titles=self.titles


    
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
        self.titles=[]
        pub.subscribe(self.set_titles, "set_titles")
        pub.subscribe(self.display_html, "display_html")

    def set_titles(self, user_input):
        self.title.set_titles()
        self.titles = self.title.get_titles()
        apc.prompt=user_input
        #print(f"Titles: {self.titles}")
        self.display_html()
    def display_html(self):
        #print("Titles_Controller: display_html")
        titles_html= """<button id="titles-button"  onclick="showTitles({tid},{toid})" style="position: absolute; left: 0;">Titles</button>
<table>"""
        for tid, title in enumerate(self.titles):
            print   (f"display_html: Title: {tid}. {title}")

            if tid in self.topic.topics:
                #print(f"display_html: topic.topics: {tid}")
                #exit(   )
                topics = self.topic.topics[tid]
                topics_html ="<table>"

                
                for toid, topic in enumerate(topics):
                    #print(f"display_html: Title: {tid} Topic: {toid}. {topic}")  

                    if tid in self.section.sections:
                        section_html = "<table>"
                        pp(self.section.sections)                        
                        print(f"tid in section: {tid}")
                        if toid in self.section.sections[tid]:
                            print(f"toid in section.sections: {toid}")
                            for sid, section in enumerate(self.section.sections[tid][toid]):
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

                    topics_html += f'''<tr><td class="td-cell"><button id="use-button"  onclick="useTopic({tid},{toid})"><<<</button></td>
                    <td> </td><td><a id="topic_{tid}_{toid}"></a><span class="{topic_border}">{topic}</span>
                    <br>
                    <button id="sections-button"  onclick="sectionsButtonClicked({tid},{toid})">sections</button> <br>
                    {section_html}
                    </td></tr>''' 
                
                topics_html +="</table>"
            else:
                topics_html = "No topics"
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