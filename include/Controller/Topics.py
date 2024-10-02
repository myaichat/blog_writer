
import wx
from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Titles import Titles_Controller
import include.config.init_config as init_config 

class notImplementedError(Exception):
    pass

apc = init_config.apc
log=apc.log
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
    def __init__(self):
        self.topics = {}
        #self.set_topics()
  

    def set_topics(self, title_id):
        if apc.mock:
            self.topics[title_id] = mocked_topics[title_id]
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
        