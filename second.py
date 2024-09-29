#!/usr/bin/env python
# coding: utf-8

# # Lesson 3: Reflection and Blogpost Writing

# ## Setup

# In[1]:
llm_config = {"model": "gpt-3.5-turbo"}
#llm_config = {"model": "gpt-4o-mini"}


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

# In[2]:
task = f'''
        Assuming blog title is: "{title}"
        and Final Refined List of Blog Headline Suggestions:
        {topics}.
        Also given the following introduction:
        {intro}
        Write concise but engaging second section of the blog:
         "2. The Power of Collaboration: Uniting Experts in the AI Space".
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
