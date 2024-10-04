import wx
import wx.html2
import os
import json
import shutil
from os.path import isfile, isdir, join

from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Topics import Topics_Controller
class notImplementedError(Exception):
    pass

import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log

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


mocked_sections={}
mocked_sections["0"]={}
mocked_sections["0"]["0"]=['''The Vision Behind DeepLearning.AI's Community Initiatives
        At DeepLearning.AI, we envision a future where artificial intelligence 
        flourishes through collaboration and active community engagement. 
        Our mission is to cultivate a dynamic ecosystem that unites experts,
        learners, and enthusiasts alike, empowering them to share knowledge and 
        drive innovation together. By prioritizing partnerships and fostering 
        inclusive initiatives, we strive to make AI accessible and impactful for 
        everyone. In this blog, we invite you to explore the collaborative efforts 
        that are nurturing a thriving AI community and inspiring the next generation 
        of technological breakthroughs.''',
        '''At the heart of DeepLearning.AI’s mission is a commitment to fostering diversity and inclusion in AI. Recognizing the underrepresentation of certain groups in the tech industry, the company has launched initiatives to empower underrepresented communities by providing access to education, mentorship, and professional opportunities. Through collaborations with organizations focused on diversity, DeepLearning.AI works to build an inclusive AI community where diverse perspectives contribute to innovations that benefit everyone. This vision is not just about filling technical gaps but also about ensuring that AI solutions are reflective of the world’s diverse population.''',
        '''DeepLearning.AI’s community initiatives are centered around creating a collaborative ecosystem where learners, researchers, and professionals can share knowledge and experiences. By organizing virtual events, meetups, and forums, the organization fosters an environment where AI enthusiasts can collaborate on projects, seek mentorship, and exchange ideas. This ecosystem nurtures a spirit of learning, where individuals can leverage collective wisdom to solve complex problems. The vision is to build a robust AI community that grows together, pushing the boundaries of what is possible in AI research, development, and real-world application.''',
        '''One of DeepLearning.AI’s core values is leveraging AI for social good. Through its community initiatives, the organization encourages collaboration between AI practitioners and nonprofits, researchers, and policymakers to tackle global challenges such as climate change, healthcare accessibility, and education. By empowering its community to participate in these socially impactful projects, DeepLearning.AI aims to drive positive change through AI. These initiatives focus on making AI technologies accessible and applicable to humanitarian causes, aligning with a broader vision of using AI to create a better world for future generations.''',
        '''DeepLearning.AI is deeply invested in nurturing the next generation of AI leaders. Through mentorship programs, internships, and collaborative research projects, the organization provides hands-on experiences for learners to develop their skills while receiving guidance from seasoned professionals. This initiative reflects a commitment to long-term growth and sustainability in the AI ecosystem. By mentoring future AI leaders, DeepLearning.AI ensures that the community continues to innovate and advance the field, ultimately creating a positive ripple effect in industries and communities worldwide. This vision supports both individual growth and the collective advancement of AI.''',

        ]

mocked_sections["0"]["1"]=['''The Vision Behind DeepLearning.AI's Community Initiatives
        At DeepLearning.AI, we envision a future where artificial intelligence 
        flourishes through collaboration and active community engagement. 
        Our mission is to cultivate a dynamic ecosystem that unites experts,
        learners, and enthusiasts alike, empowering them to share knowledge and 
        drive innovation together. By prioritizing partnerships and fostering 
        inclusive initiatives, we strive to make AI accessible and impactful for 
        everyone. In this blog, we invite you to explore the collaborative efforts 
        that are nurturing a thriving AI community and inspiring the next generation 
        of technological breakthroughs.''',
        '''At the heart of DeepLearning.AI’s mission is a commitment to fostering diversity and inclusion in AI. Recognizing the underrepresentation of certain groups in the tech industry, the company has launched initiatives to empower underrepresented communities by providing access to education, mentorship, and professional opportunities. Through collaborations with organizations focused on diversity, DeepLearning.AI works to build an inclusive AI community where diverse perspectives contribute to innovations that benefit everyone. This vision is not just about filling technical gaps but also about ensuring that AI solutions are reflective of the world’s diverse population.''',
        '''DeepLearning.AI’s community initiatives are centered around creating a collaborative ecosystem where learners, researchers, and professionals can share knowledge and experiences. By organizing virtual events, meetups, and forums, the organization fosters an environment where AI enthusiasts can collaborate on projects, seek mentorship, and exchange ideas. This ecosystem nurtures a spirit of learning, where individuals can leverage collective wisdom to solve complex problems. The vision is to build a robust AI community that grows together, pushing the boundaries of what is possible in AI research, development, and real-world application.''',
        '''One of DeepLearning.AI’s core values is leveraging AI for social good. Through its community initiatives, the organization encourages collaboration between AI practitioners and nonprofits, researchers, and policymakers to tackle global challenges such as climate change, healthcare accessibility, and education. By empowering its community to participate in these socially impactful projects, DeepLearning.AI aims to drive positive change through AI. These initiatives focus on making AI technologies accessible and applicable to humanitarian causes, aligning with a broader vision of using AI to create a better world for future generations.''',
        '''DeepLearning.AI is deeply invested in nurturing the next generation of AI leaders. Through mentorship programs, internships, and collaborative research projects, the organization provides hands-on experiences for learners to develop their skills while receiving guidance from seasoned professionals. This initiative reflects a commitment to long-term growth and sustainability in the AI ecosystem. By mentoring future AI leaders, DeepLearning.AI ensures that the community continues to innovate and advance the field, ultimately creating a positive ripple effect in industries and communities worldwide. This vision supports both individual growth and the collective advancement of AI.''',

        ]
class Section():
    sections=MutableDictAttribute()
    def __init__(self):
        self.init()
        assert apc.blog_name, 'Blog name not set'
        self.log_dir = log_dir=join('log', apc.blog_name)
        self.latest_dir=latest_dir=join(log_dir, 'latest')
        ts=apc.ts
        
        self.sections_fn=sections_fn=join(latest_dir, f'sections_{ts}.json')          
        if not isdir(latest_dir):
            os.makedirs(latest_dir)
 

        if 1:
            self.reset()

    def set_sections(self, title_id, topic_id):
        
        if apc.mock:
            if apc.current_title not in  self.sections:
                self.sections[apc.current_title]={}
            if title_id not in self.sections[apc.current_title]:
                self.sections[apc.current_title][title_id] = {}
            self.sections[apc.current_title][title_id][topic_id] = {str(i):{'section':x, 'tid':title_id, 'toid':topic_id} for i, x in enumerate(mocked_sections[title_id][topic_id])} 
            log(f"Mocked Sections set")
        else:
            raise Exception("Not implemented")
        apc.sections=self.sections[apc.current_title]


    def get_sections(self, title_id, topic_id):
        if  apc.current_title not in  self.sections:
            return None
        sections  = self.sections[apc.current_title].get(title_id, None)
        if not sections:
            return None
        return sections.get(topic_id, None) 
    def init(self):
        self.cfg={}
        self.mta=set()
        self.dump_file={}


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
        files = [f for f in files if f.startswith('sections') and f.endswith('.json')]
        pp(files)
        assert len(files) <= 1, ('Should be only one latest file', files)
        if files:
            assert isfile(join(latest_dir, files[0])), ('Should be a file', files[0])
            shutil.copy(join(latest_dir, files[0]), join(log_dir, files[0]))
            os.rename(join(latest_dir, files[0]), self.sections_fn)
            if hard:
                os.remove(self.sections_fn)
                assert not isfile(self.topics_fn), self.sections_fn
                self.sections_fn=join(latest_dir, f'topics_{apc.ts}_reset.json')
                self.init()
                       
        self.sections=self.get_attr('sections', {apc.current_title:{}}, self.sections_fn)
        apc.sections=self.sections[apc.current_title]


    
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
    
    
class Sections_Controller(Topics_Controller):  
    def __init__(self):
        Topics_Controller.__init__(self)
        self.section = Section()
        
        pub.subscribe(self.set_sections, "set_sections")

    def set_sections(self, title_id, topic_id):
        print(f"set_sections: Title ID: {title_id} topic_id {topic_id}")
        self.section.set_sections(title_id, topic_id)
        
        self.sections = self.section.get_sections(title_id, topic_id)
        #pp(self.topics)
        #print(f"topics: {self.topics}")
        pub.sendMessage("display_html")
        print(f"end of set_sections")
        #self.display_html()
        self.web_view.RunScriptAsync(f"window.location.href = '#topic_{title_id}_{topic_id}';")