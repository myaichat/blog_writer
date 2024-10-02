
import wx
from pubsub import pub
from pprint import pprint as pp 
class notImplementedError(Exception):
    pass

import include.config.init_config as init_config 

apc = init_config.apc
log=apc.log
class Title():
    def __init__(self):
        self.set_titles()

    def set_titles(self):
        if apc.mock:
            self.titles = [ "Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI",
            "Empowering the Next Generation: DeepLearning.AI's Role in AI Education and Workforce Development",
            "Leading the Way: Groundbreaking Research and Innovations from DeepLearning.AI",
            "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI",
            "Ethics in AI: DeepLearning.AI's Journey Towards Responsible and Fair Artificial Intelligence"]
            log('Mock Titles set')
        else:
            raise NotImplementedError
        apc.titles=self.titles

    def get_titles(self):
        return self.titles

    def __repr__(self):
        return self.titles
    def reset(self):
        self.stitles=[]
        
    
class Titles_Controller():  
    def __init__(self):
        self.title = Title()
        self.titles=[]
        pub.subscribe(self.set_titles, "set_titles")
        pub.subscribe(self.display_html, "display_html")

    def set_titles(self, user_input):
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
                    window.location.href = 'app:show_start:0';
                }  
                function previewButtonClicked() {
                    console.log('reset button clicked');
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