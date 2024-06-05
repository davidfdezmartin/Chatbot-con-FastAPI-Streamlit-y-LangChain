from langchain.agents import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.utilities import WikipediaAPIWrapper, ArxivAPIWrapper

def create_custom_tools_agent(model, tools, prompt_template):
    agent_tools = [Tool(name="Wikipedia", func=tools[0].run, description="Busca información en Wikipedia"),
                   Tool(name="Arxiv", func=tools[1].run, description="Busca artículos académicos en Arxiv")]

    agent = ChatPromptTemplate(model=model, tools=agent_tools, prompt_template=prompt_template)
    return agent
