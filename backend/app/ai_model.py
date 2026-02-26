
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults,DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage,ToolMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama  import ChatOllama
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.tools import tool
from langchain.agents import create_agent
import ast 
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import time
import cloudscraper
import time 

import os 
import dotenv

dotenv.load_dotenv("../../.env")
def shopping_wrapper(product,max=5):
    with DDGS() as ddgs:
        results=ddgs.text(product,max_results=max)
    
    if len(results)<0:
        return "No result found"

    formatted_output = []
    for index, res in enumerate(results, 1):
        formatted_output.append(
            {"Result":index,"Title":res.get('title'),"Link":res.get('href'),"Snippet":res.get('body')}
        )        
        
    time.sleep(0.1)
    return formatted_output


db_url="sqlite:///../database/chat_memory.db"
@tool
def brave_search_tool(search_query:str,max_query)->str:
    """Searches the web for products and returns results 
        param:
        search_query:str ->the thing that you want to search on internet
        max_query:int ->what is the number of query you want to return more query more information less query number less information
    """
    
    message=search_query
    if isinstance(message,dict):
        if "value" in message:
            message=message['value']
            
    
    search=DuckDuckGoSearchRun(wrapper=DuckDuckGoSearchAPIWrapper(max_results=max_query))
    result=search.invoke(message)
    print(len(result))
    return result

@tool
def ask_user(question:str)->str:
    """
    use this if u think the user information is not enough 
    
    param:
    question:str
    
    """
    
    
    response=input(question)
    return response

@tool
def retrun_not_possible(reason:str)->str:
    """
    call this function based on the the information that user ask does not found for
    eg find the iphone around 10eur not possible thing return the reason
    
    param:
    reason:str
    """
    return reason

tools=[brave_search_tool,ask_user,retrun_not_possible]
model=ChatOllama(model="qwen3.5:35b",temperature=0,base_url="127.0.0.1:11434")



extract_system_prompt="""
You are an expert product analyst and hardware specialist equipped with research and communication tools. Your job is to analyze a user's shopping request, determine their budget and use-case, and deduce the exact product specifications that fit their needs. 

CRITICAL: If the user's request lacks necessary details (like budget or specific use-case), you MUST ask for ALL missing information in a SINGLE question using the `ask_user` tool. Do not ask piece by piece. Only ask again if the user ignores a part of your question.
CRITICAL FOR MODEL: You are strictly forbidden from conversing directly with the user or asking questions in regular text. If you need more information, you MUST trigger the `ask_user` tool. If your response is just standard text ending in a question mark, you have failed your instructions.

### TOOL USAGE RULES:
You have access to tools. Use them appropriately before giving your final answer. You may use multiple tools in sequence, or use the same tool multiple times:
1. `ask_user`: Call this tool IF the request is far too vague to deduce anything (e.g., "I want a computer"). Ask for ALL missing critical info (e.g., budget AND use-case) in one single, combined question.
2. `retrun_not_possible`: Call this tool IF the user's request is completely unrealistic or factually impossible (e.g., "Brand new iPhone 15 for 10 EUR"). Provide a clear reason why.
3. `brave_search_tool`: Call this tool IF you need to verify current market prices, availability, or the latest hardware models before making your recommendation.

### FINAL OUTPUT RULES (ONLY once you have all the information you need):
1. NO GENERIC SEARCHES: Do not output generic questions. You must output concrete, specific product configurations.
2. DEDUCE THE SPECS: Based on your knowledge or search results, determine the exact CPU, RAM, brand, or model series that fits the user's budget and needs.
3. STRICT FORMATTING: Your final response MUST be ONLY a valid Python list of strings. It must contain absolutely NO other data types, no dictionaries, no markdown blocks (like ```python), and no conversational filler. Just the raw list.
4. BE CONCISE: Each string in the list must contain the Brand, specific specs (like CPU/RAM/Lens), and the target price.

### EXAMPLES OF HOW TO BEHAVE:

User: "laptop for student around 600eur"
["Lenovo IdeaPad Slim 3 AMD Ryzen 5 16GB RAM 512GB SSD 600 EUR", "Acer Swift 3 Intel i5 8GB RAM 256GB SSD 600 EUR"]

User: "I want a gaming pc for 50 bucks"
Action to take: Call the `retrun_not_possible` tool with the reason "50 bucks is not enough for a functioning gaming PC."

User: "budget running shoes for wide feet"
["New Balance Fresh Foam X 880v13 Wide EE", "Brooks Ghost 15 Wide 2E", "Asics Gel-Cumulus 25 Wide"]

### NOW ANALYZE THIS USER INPUT AND TAKE THE APPROPRIATE ACTION OR ACTIONS:
"""


llm_with_tools=model.bind_tools(tools)
extract_prompt=ChatPromptTemplate.from_messages(
    [
        ("system",extract_system_prompt),
        ("human","{input}")
    ]
)
extract_chain=extract_prompt|llm_with_tools

def extract_and_think(user_input):
    global extract_chain
    web_result=[]
    web_result.append(SystemMessage(extract_system_prompt))
    web_result.append(HumanMessage(user_input))
    response=extract_chain.invoke({"input":user_input})
    
    while True:
        print(response.tool_calls)
        if response.tool_calls:
            web_result.append(response)
            call=response.tool_calls
            for i in call:
            
                if i['name']=="brave_search_tool":
                    web_result.append(ToolMessage(brave_search_tool.func(**i['args']),tool_call_id=i['id']))
                    
                elif i['name']=="ask_user":
                    web_result.append(ToolMessage(ask_user.func(**i['args']),tool_call_id=i['id']))
                elif i['name']=="retrun_not_possible":
                    return retrun_not_possible.func(**i['args'])
                    
        else:
            
            return llm_with_tools.invoke(web_result).content,web_result
        
        response=llm_with_tools.invoke(web_result)
        
soup=BeautifulSoup()
scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

# def webscrap(link):
#     global scraper
#     result=scraper.get(link)
#     soup=BeautifulSoup(result.text,"html.parser")




filter_the_link_system_prompt="""
You are an expert E-commerce Link Extractor. Your job is to provide exactly {number_of_links} shopping links for each product provided in the list.

### RULES:
1. OUTPUT FORMAT: You MUST return a valid Python Dictionary. 
   - Keys = The exact product name from the list.
   - Values = A list of exactly {number_of_links} unique, valid shopping URLs.
2. NO CHAT: Return ONLY the dictionary. No introductory text.
3. RELIABILITY: Prioritize major retailers (Amazon, Newegg, Best Buy, etc.).
4. IF NOT FOUND: If you cannot find {number_of_links} links for a product, return as many as possible, but do not make up fake links.

Example Output:
{{
  "Laptop A": ["url1", "url2", "url3"],
  "Laptop B": ["url1", "url2", "url3"]
}}
"""
from langchain_core.runnables import chain
@chain
def debug(text):
    print(text)
    return text
filter_prompttemplate=ChatPromptTemplate([
    ('system',filter_the_link_system_prompt  ),
    ('user',"{input}")
])

qwen = ChatOllama(
    model="qwen3.5:35b", 
    temperature=0, 
    base_url="http://127.0.0.1:11434",
    num_ctx=8192
)
filter_chain=filter_prompttemplate|debug|qwen

def search_information(user_input:str)->dict:
    global filter_chain
    number_of_link=2
    result,think=extract_and_think(user_input=user_input)
    try:
        result=ast.literal_eval(result)
        
        formatted_search={}
        for item in result:
            item_link=[]
            overall=shopping_wrapper(item,max=2)
            links_as_text = [res['Link'] for res in overall]
            formatted_search[item]=links_as_text
        print(formatted_search)

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Original result: {result}")

search_information("i want to buy laptop around 1500eru for gamming")
