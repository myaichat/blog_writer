#!/usr/bin/env python
# coding: utf-8

# # Lesson 3: Reflection and Blogpost Writing

# ## Setup

# In[1]:
llm_config = {"model": "gpt-3.5-turbo"}
llm_config = {"model": "gpt-4o-mini"}


# ## The task!
title= "Building a Thriving Community: Collaborations and Initiatives at DeepLearning.AI"
topics= """
    1. Introduction: The Vision Behind DeepLearning.AI's Community Initiatives
    2. The Power of Collaboration: Uniting Experts in the AI Space
    3. Empowering the Next Generation: Educational Initiatives at DeepLearning.AI
    4. Bridging Gaps: Fostering Inclusivity in AI Communities
    5. Conclusion: Sustaining Growth and Cultivating Connections in the AI Community
"""
intro ="""
>>>
### Introduction: The Vision Behind DeepLearning.AI's Community Initiatives
At DeepLearning.AI, we envision a future where artificial intelligence flourishes through collaboration and active community engagement. Our mission is to cultivate a dynamic ecosystem that unites experts, learners, and enthusiasts alike, empowering them to share knowledge and drive innovation together. By prioritizing partnerships and fostering inclusive initiatives, we strive to make AI accessible and impactful for everyone. In this blog, we invite you to explore the collaborative efforts that are nurturing a thriving AI community and inspiring the next generation of technological breakthroughs.
<<<
"""
second="""
>>>
### The Power of Collaboration: Uniting Experts in the AI Space

Collaboration is the backbone of DeepLearning.AI's mission, fueling innovation and progress in the AI field. 
By uniting experts from various sectors—academia, industry, and research—we foster a rich environment where diverse ideas can thrive.
 Our initiatives, such as joint research projects and collaborative workshops, facilitate knowledge sharing and merge different perspectives. 
 This collective effort not only accelerates the creation of groundbreaking solutions but also elevates the community's overall expertise. 
 Together, we demonstrate that collaboration is essential for shaping a vibrant future in artificial intelligence.
<<<
"""
third="""

>>>
### Empowering the Next Generation: Educational Initiatives at DeepLearning.AI

At DeepLearning.AI, we are dedicated to empowering the next generation through innovative educational initiatives. Our diverse offerings, 
including online courses, scholarships, and mentorship programs, equip learners with essential skills for the AI landscape. 
Collaborating with universities and organizations across the globe, we strive to make quality education accessible to all. 
Our hands-on approach ensures students gain practical experience while exploring AI’s immense potential. By investing in their future,
 we cultivate a community of knowledgeable innovators ready to tackle tomorrow's challenges, paving the way for a brighter AI-driven world.
<<<

"""

forth="""
>>>
### Building Inclusive AI Communities through Bridging Gaps

Diversity and inclusivity are the cornerstones of innovation in AI. DeepLearning.AI is dedicated to cultivating an environment where individuals 
from all backgrounds thrive. Our focus on mentorship programs and diversity scholarships ensures that underrepresented voices have a platform to shine. 
By embracing inclusivity, we not only broaden our collective knowledge but also pave the way for a more equitable and innovative future in artificial 
intelligence. Join us as we bridge gaps, foster inclusivity, and celebrate the richness that diversity brings to our AI communities.
 Together, we can create a brighter and more inclusive tomorrow.
<<<
"""

# In[2]:
task = f'''
        Assuming blog title is: "{title}"
        and Final Refined List of Blog Headline Suggestions:
        {topics}.
        Also given the following introduction:
        {intro}
        Also answerred  the second section of the blog:
        {second}    
        Also answerred  the third section of the blog:
        {third} 
        Also answerred  the forth section of the blog:
        {forth}                      
        Write concise but engaging fifth section of the blog (Conclusion):
         "5. Conclusion: Sustaining Growth and Cultivating Connections in the AI Community".
        Make sure your outputt is within 100 words. 
       '''


# ## Create a writer agent

# In[3]:
import autogen



writer = autogen.AssistantAgent(
    name="Writer",
    system_message="You are a writer. You write engaging and concise " 
        "blogpost (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    llm_config=llm_config,
)

# In[4]:
reply = writer.generate_reply(messages=[{"content": task, "role": "user"}])


# In[5]:
print("Initial Writer Response:")
print(reply)


# ## Adding reflection 
# 
# Create a critic agent to reflect on the work of the writer agent.

# In[6]:
critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive feedback to help improve the quality of the content.",
)


# In[7]:
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)


# ## Nested chat

# In[8]:
SEO_reviewer = autogen.AssistantAgent(
    name="SEO Reviewer",
    llm_config=llm_config,
    system_message="You are an SEO reviewer, known for your ability to optimize content for search engines, "
        "ensuring that it ranks well and attracts organic traffic. "
        "Make sure your suggestion is concise (within 3 bullet points), concrete and to the point. "
        "Begin the review by stating your role.",
)


# In[9]:
legal_reviewer = autogen.AssistantAgent(
    name="Legal Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer, known for your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), concrete and to the point. "
        "Begin the review by stating your role.",
)


# In[10]:
ethics_reviewer = autogen.AssistantAgent(
    name="Ethics Reviewer",
    llm_config=llm_config,
    system_message="You are an ethics reviewer, known for your ability to ensure that content is ethically sound "
        "and free from any potential ethical issues. "
        "Make sure your suggestion is concise (within 3 bullet points), concrete and to the point. "
        "Begin the review by stating your role.",
)


# In[11]:
meta_reviewer = autogen.AssistantAgent(
    name="Meta Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggregate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)


# ## Orchestrate the nested chats to solve the task

# In[12]:
def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''


# Ensure that message names comply with naming rules (alphanumeric, underscore, hyphen)
def reflection_message(recipient, messages, sender, config):
    # Ensure the name is correctly formatted without invalid characters
    return f'''Review the following content: 
    \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

def reflection_message(recipient, messages, sender, config):
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
     "recipient": SEO_reviewer, 
     "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
     "max_turns": 1},
    {
    "recipient": legal_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": ethics_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
     {"recipient": meta_reviewer, 
      "message": "Aggregate feedback from all reviewers and give final suggestions on the content.", 
     "max_turns": 1},
]


# In[13]:
critic.register_nested_chats(
    review_chats,
    trigger=writer,
)


# **Note**: You might get a slightly different response than what's shown in the video. Feel free to try a different task.

# In[ ]:
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)


# ## Get the summary

# In[ ]:
print("Final Refined List of Blog Headline Suggestions:")
print(res.summary)
