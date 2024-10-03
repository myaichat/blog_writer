
import wx
import os, sys, json, shutil
from  os.path import isfile, isdir, join
from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Titles import Titles_Controller
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


mocked_topics={}
mocked_topics[0]=['Introduction: The Vision Behind DeepLearning.AI''s Community Initiatives',
    'The Power of Collaboration: Uniting Experts in the AI Space',
    'Empowering the Next Generation: Educational Initiatives at DeepLearning.AI',
    'Bridging Gaps: Fostering Inclusivity in AI Communities',
    'Conclusion: Sustaining Growth and Cultivating Connections in the AI Community']
mocked_topics[1]=[ 'Introduction:AI in Healthcare: Enhancing Diagnosis and Patient Care with Deep Learning',
    'Retail Revolution: How AI Personalization is Shaping Customer Experience',
    'AI in Finance: Automating Risk Management and Fraud Detection',
    'Smart Manufacturing: AI-Driven Efficiency and Predictive Maintenance',
    'Conclusion:Transforming Marketing Strategies with AI-Powered Consumer Insights']
mocked_topics[2]=['Intro:Pioneering Natural Language Processing: Transforming Human-Computer Interaction',
    'Reinforcement Learning Breakthroughs: Shaping Autonomous Systems and Robotics',
    'AI for Climate Change: Innovations in Environmental Monitoring and Prediction',
    'Advancements in Computer Vision: Revolutionizing Image Recognition and Analysis',
    'Conclusion:Ethics in AI: DeepLearning.AI''s Role in Developing Responsible AI Solutions']
mocked_topics[3]=['Intro:Global AI Education: Expanding Access to AI Learning Through Partnerships',
'Empowering Women in AI: DeepLearning.AI''s Role in Promoting Diversity and Inclusion',
'AI for Social Good: Collaborative Projects Tackling Global Challenges',
'The AI Educators'' Network: Fostering Knowledge Sharing and Professional Growth',
'Conclusion:Mentorship Programs: Building the Next Generation of AI Leaders Through Community Support']
class Topic():
    topics=MutableDictAttribute()
    def __init__(self):
        self.init()
        assert apc.blog_name, 'Blog name not set'
        self.log_dir = log_dir=join('log', apc.blog_name)
        self.latest_dir=latest_dir=join(log_dir, 'latest')
        ts=apc.ts
        
        self.topics_fn=topics_fn=join(latest_dir, f'topics_{ts}.json')          
        if not isdir(latest_dir):
            os.makedirs(latest_dir)
 

        if 0:
            self.reset()
  

    def set_topics(self, title_id):
        print('apc.mock',apc.mock)
        if apc.mock:
            self.topics[title_id] = mocked_topics[title_id]
            log(f"Mocked topics set")
        else:
            raise NotImplementedError
        apc.topics=self.topics


    def get_topics(self, title_id):
        return self.topics[title_id]

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
        files = [f for f in files if f.startswith('topics') and f.endswith('.json')]
        pp(files)
        assert len(files) <= 1, ('Should be only one latest file', files)
        if files:
            assert isfile(join(latest_dir, files[0])), ('Should be a file', files[0])
            shutil.copy(join(latest_dir, files[0]), join(log_dir, files[0]))
            os.rename(join(latest_dir, files[0]), self.topics_fn)
            if hard:
                os.remove(self.topics_fn)
                assert not isfile(self.topics_fn), self.topics_fn
                self.topics_fn=join(latest_dir, f'topics_{apc.ts}_reset.json')
                self.init()
                       
        self.topics=self.get_attr('topics', {}, self.topics_fn)
        apc.topics=self.topics


    
    def get_attr(self, attr, default=None, dump_file='.config.json'): 
        if attr not in self.dump_file:
            self.dump_file[attr]=dump_file
        config_fn=self.dump_file[attr]
        self.mta.add(attr)
        print('-------------------config_fn: ' , attr, config_fn)
        if config_fn not in self.cfg:
            self.cfg[config_fn]={}
        cfg=self.cfg[config_fn]
        pp(cfg)
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
                            data=cfg=cfg_dump
                            if 1:
                                self.cfg[config_fn]['topics']={int(k):v for k,v in data['topics'].items()}
                                cfg=self.cfg[config_fn]
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
        pp(attr)
        pp(value)
        print('Dumping ******************************:', attr, dump_file)    
        with open(dump_file, 'w') as f:
            json.dump(cfg, f, indent=2)    

class Topics_Controller(Titles_Controller):  
    def __init__(self):
        Titles_Controller.__init__(self)
        self.topic = Topic()
        self.topics={}
        pub.subscribe(self.set_topics, "set_topics")

    def set_topics(self, title_id):
        print(f"set_topics: Title ID: {title_id}")
        self.topic.set_topics(title_id)
        self.topics = self.topic.get_topics(title_id)
        #pp(self.topics)
        #print(f"topics: {self.topics}")
        #Titles_Controller.display_html(self)
        pub.sendMessage("display_html")

        self.display_html()
        self.web_view.RunScriptAsync(f"window.location.href = '#title_{title_id}';")
        