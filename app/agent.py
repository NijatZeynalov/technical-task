import os
from typing import List, Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, ConfigDict
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool


class TicketCategory(BaseModel):
    """The category of the ticket."""
    tags: List[str] = Field(
        description="A list of tags that best describe the ticket. For example, ['Hardware', 'Printer'] or ['Access', 'Account'].",
        json_schema_extra={"example": ["Hardware", "Printer"]}
    )

# this @tool decorator makes the function available to the agent.
@tool
def get_ticket_category(description: str, title: str) -> TicketCategory:
    """
    Analyzes the ticket title and description to determine the best category tags.
    """
    # In a real-world scenario, this function will contain more complex logic
    # For now I just relying on the LLM's ability to categorize based on the provided text.
    print(f"TOOL CALLED: get_ticket_category with title: '{title}' and description: '{description[:30]}...'")
    # The actual categorization is done by the LLM through function calling,
    # so this function just returns the data in the expected format.
    # The 'tags' will be populated by the LLM's tool call.
    return TicketCategory(tags=[])


# --- 2. Agent ---
# it uses an LLM to understand the user's
# request, decides which tool to call, executes the tool, and returns the result.

class TicketAgent:
    def __init__(self):
        # Initialize the LLM. I use a small phi3 model for demo purpose. Originally, llama3.1 and other models has ability for tool calling.
        try:
            llm = ChatOllama(model="phi3", temperature=0)
            
            # list of tools available to the agent.
            tools = [get_ticket_category]
            
            #  the prompt template for the agent.
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are a helpful assistant that categorizes helpdesk tickets."),
                    ("human", "{input}"),
                    ("placeholder", "{agent_scratchpad}"),
                ]
            )
            
            #  the tool-calling agent.
            agent = create_tool_calling_agent(llm, tools, prompt)
            
            #  the agent executor, which runs the agent and its tools.
            self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            self.use_agent = True
            print("TicketAgent initialized with LangChain and Ollama.")
        except Exception as e:
            print(f"Failed to initialize agent with tools: {e}")
            print("Falling back to simple LLM approach.")
            self.use_agent = False
            try:
                self.llm = ChatOllama(model="phi3", temperature=0)
                print("TicketAgent initialized with simple LLM approach.")
            except Exception as e2:
                print(f"Failed to initialize LLM: {e2}")
                self.llm = None
                print("TicketAgent will use rule-based tagging.")

    def _rule_based_tagging(self, title: str, description: str) -> List[str]:
        """Fallback rule-based tagging when LLM is not available. In our case."""
        text = (title + " " + description).lower()
        tags = []
        
        # Hardware related
        if any(word in text for word in ["printer", "computer", "laptop", "monitor", "keyboard", "mouse"]):
            tags.append("Hardware")
        
        # Software related
        if any(word in text for word in ["software", "application", "program", "login", "password", "account"]):
            tags.append("Software")
        
        # Network related
        if any(word in text for word in ["internet", "network", "wifi", "connection", "email"]):
            tags.append("Network")
        
        # Access related
        if any(word in text for word in ["access", "permission", "login", "account", "password"]):
            tags.append("Access")
        
        # If no specific tags found, add general
        if not tags:
            tags.append("General")
            
        return tags

    def process_ticket(self, title: str, description: str) -> List[str]:
        """
        Processes a new ticket to automatically add tags using an LLM agent.
        """
        print(f"AGENT: Processing ticket '{title}'")
        
        if self.use_agent:
            try:
                prompt = f"Please categorize the following ticket. Title: '{title}', Description: '{description}'"
                
                # Invoke the agent to get the result.
                response = self.agent_executor.invoke({"input": prompt})
                
                # The output from the tool call is a list of dictionaries.
                # let's parse it to extract the tags.
                if "output" in response and response["output"]:
                    # Assuming the tool returns a list with one TicketCategory object
                    tool_output = response["output"][0]
                    if isinstance(tool_output, TicketCategory):
                        tags = tool_output.tags
                        print(f"AGENT: Tags found: {tags}")
                        return tags
                
                print("AGENT: No tags were generated by the agent.")
                return ["General"]

            except Exception as e:
                print(f"AGENT: An error occurred during agent execution: {e}")
                print("AGENT: Falling back to simple LLM approach.")
                self.use_agent = False
        
        if self.llm and not self.use_agent:
            try:
                # Simple LLM approach without tools
                prompt = f"Please categorize this ticket and return only a JSON array of tags (max 3 tags). Title: '{title}', Description: '{description}'. Example response: ['Hardware', 'Printer']"
                response = self.llm.invoke(prompt)
                content = response.content
                
                # Try to extract tags from the response
                try:
                    import re
                    import json
                    
                    # Find JSON array pattern
                    json_match = re.search(r'\[.*?\]', content)
                    if json_match:
                        tags = json.loads(json_match.group())
                        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
                            print(f"AGENT: LLM generated tags: {tags}")
                            return tags[:3]  # Limit to 3 tags
                except:
                    pass
                
                # If JSON parsing fails, try to extract meaningful words
                words = content.lower().split()
                potential_tags = []
                for word in words:
                    if word in ["hardware", "software", "network", "access", "printer", "computer", "email", "login"]:
                        potential_tags.append(word.title())
                
                if potential_tags:
                    print(f"AGENT: Extracted tags from LLM response: {potential_tags}")
                    return potential_tags[:3]
                
            except Exception as e:
                print(f"AGENT: An error occurred during LLM processing: {e}")
        
        # Fallback to rule-based tagging
        print("AGENT: Using rule-based tagging.")
        return self._rule_based_tagging(title, description)

