import wx
from pubsub import pub
from pprint import pprint as pp 
from include.Controller.Topics import Topics_Controller
class notImplementedError(Exception):
    pass

import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log

mocked_sections={}
mocked_sections[0]={}
mocked_sections[0][0]=['''### Introduction: The Vision Behind DeepLearning.AI's Community Initiatives
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
    def __init__(self):
        self.sections = {}
        #self.set_topics()

    def set_sections(self, title_id, topic_id):
        self.sections[int(title_id)]={}
        if apc.mock:
            
            self.sections[int(title_id)][int(topic_id)] = mocked_sections[int(title_id)][int(topic_id)] 
            log(f"Mocked Sections set")
        else:
            raise Exception("Not implemented")
        apc.sections=self.sections


    def get_sections(self, title_id, topic_id):
       
        return self.sections[title_id][topic_id] 
    def reset(self):
        self.sections={}    
    
    
class Sections_Controller(Topics_Controller):  
    def __init__(self):
        Topics_Controller.__init__(self)
        self.section = Section()
        self.sections={}
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