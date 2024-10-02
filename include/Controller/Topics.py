
import wx
from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Titles import Titles_Controller
import include.config.init_config as init_config 

class notImplementedError(Exception):
    pass

apc = init_config.apc
log=apc.log
class Topic():
    def __init__(self):
        self.topics = {}
        #self.set_topics()

    def set_topics(self, title_id):
        if apc.mock:
            self.topics[title_id] = ['Introduction: The Vision Behind DeepLearning.AI''s Community Initiatives',
        'The Power of Collaboration: Uniting Experts in the AI Space',
        'Empowering the Next Generation: Educational Initiatives at DeepLearning.AI',
        'Bridging Gaps: Fostering Inclusivity in AI Communities',
        'Conclusion: Sustaining Growth and Cultivating Connections in the AI Community']
            log(f"Mocked topics set")
        else:
            raise NotImplementedError
        apc.topics=self.topics


    def get_topics(self, title_id):
        return self.topics[title_id]

    def __repr__(self):
        return self.topics
    def reset(self):
        self.topics={}    
    
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
        