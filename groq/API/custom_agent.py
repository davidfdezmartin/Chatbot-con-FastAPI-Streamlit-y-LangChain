from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.llms.base import LLM
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
from langchain.chains import LLMChain
from langchain.tools.base import BaseTool

class CustomAgent(LLMSingleActionAgent):
    @property
    def input_keys(self):
        return ["input"]

    def plan(self, intermediate_steps, **kwargs):
        return AgentAction(tool=intermediate_steps[-1][0], tool_input=intermediate_steps[-1][1], log="")

class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        else:
            return AgentAction(tool=llm_output, tool_input=llm_output, log=llm_output)

def create_custom_tools_agent(model: LLM, tools: List[BaseTool], prompt: PromptTemplate):
    tool_names = [tool.name for tool in tools]
    tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

    prefix = f"""Answer the following questions as best you can. You have access to the following tools:

{tool_strings}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{", ".join(tool_names)}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought:"""

    suffix = """
Thought: I now know the final answer
Final Answer:"""

    prompt_template = StringPromptTemplate(input_variables=["input", "agent_scratchpad"], template=prefix + "{agent_scratchpad}" + suffix)

    llm_chain = LLMChain(llm=model, prompt=prompt_template)
    output_parser = CustomOutputParser()
    agent = CustomAgent(llm_chain=llm_chain, output_parser=output_parser, allowed_tools=tool_names)

    return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
