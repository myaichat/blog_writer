
# Blog Writer - AI-Assisted Blog Creation Tool

Welcome to **Blog Writer**, an intuitive and AI-powered tool designed to streamline your blog creation process. This project leverages **wxPython** for the user interface and **OpenAI's GPT-4** model to generate blog titles, topics, and sections, making content creation both efficient and creative.

## Features

- **Title Generation**: Input a keyword or idea and generate blog titles with just a click.
- **Topic Suggestions**: Once a title is selected, generate relevant topics to guide the flow of your blog post.
- **Section Breakdown**: Each topic can be broken down into sections, allowing you to structure your blog comprehensively.
- **Real-Time Preview**: View your blog in real time as you build it, ensuring clarity and proper flow before finalizing.
- **User-Friendly UI**: Built with wxPython for a clean, intuitive interface.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/blog_writer.git
   cd blog_writer
   ```

2. Install the necessary Python libraries:
   ```bash
   pip install wxpython pubsub openai
   ```

## How to Use

1. Run the `blog_writer.py` script to launch the application:
   ```bash
   python blog_writer.py
   ```

2. Start by entering an idea or keyword, then:
   - Click **"Get Titles"** to generate blog title suggestions.
   - Choose a title by clicking on **`<<<`** next to the title of your choice.
   - Click **"topics"** to generate relevant topics under your chosen title.
   - Select a topic and click **`<<<`** to generate **sections** for that topic.
   - Click **"Preview"** at the top of the **Design** panel to view your blog in real time.

3. You can reset the design or explore new titles and topics as needed.

## Example

![Blog Writer UI](https://github.com/myaichat/blog_writer/blob/main/docs/screenshot/final_blog.png?raw=true)

In the screenshot above, a blog post titled *"Transforming Industries: How DeepLearning.AI is Revolutionizing Business with AI"* has been generated with AI-powered suggestions. The user can preview and finalize the blog in real time.
## References
[Medium article](https://medium.com/p/0c2e7caec3d7)
