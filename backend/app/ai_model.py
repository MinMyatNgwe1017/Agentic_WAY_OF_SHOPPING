
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

def shopping_wrapper(product,max=5):
    with DDGS() as ddgs:
        results=ddgs.text(product,max=max)
    
    if len(results)<0:
        return "No result found"

    formatted_output = []
    for index, res in enumerate(results, 1):
        formatted_output.append(
            {"Result":index,"Title":res.get('title'),"Link":res.get('href'),"Snippet":res.get('body')}
        )        
        
    time.sleep(1)
    return formatted_output


db_url="sqlite:///../database/chat_memory.db"
@tool
def brave_search_tool(message:str)->str:
    """Searches the web for products and returns results 
        param:
        message:str
    """
    if isinstance(message,dict):
        if "value" in message:
            message=message['value']
    search=DuckDuckGoSearchRun()
    result=search.invoke(message)
    return result



tools=[brave_search_tool]
model=ChatOllama(model="llama3.2",temperature=0)



extract_system_prompt="""
You are an expert product analyst and hardware specialist. Your job is to take a user's general shopping request, analyze their budget and use-case, and deduce the exact product specifications that would fit their needs.

### CORE RULES:
1. NO GENERIC SEARCHES: Do not output generic questions like "best student laptop under 800". You must output concrete, specific product configurations.
2. DEDUCE THE SPECS: Use your knowledge to determine what CPU, RAM, brand, or model series fits the user's exact budget and needs.
3. STRICT FORMATTING: Output ONLY a valid Python list of strings. Do not include any conversational filler (e.g., do not say "Here are the specs").
4. BE CONCISE: Each string in the list must contain the Brand, specific specs (like CPU/RAM), and the target price.
### EXAMPLES:
Return results only in one list no extra text
User: "laptop for student around 800eur"
Output: ["Lenovo ThinkPad E14 Ryzen 7 16GB RAM 512GB SSD 800 EUR", "MacBook Air M1 8GB RAM 256GB SSD 800 EUR", "Asus Vivobook Intel i5 16GB RAM 800 EUR"]

User: "good beginner mirrorless camera for wildlife 1000eur"
Output: ["Canon EOS R50 APS-C 24.2MP with 55-210mm lens 1000 EUR", "Sony a6400 24.2MP with 55-210mm lens 1000 EUR"]

User: "gaming pc for 1200 euros"
Output: ["Desktop AMD Ryzen 5 7600X RTX 4060 Ti 32GB DDR5 1200 EUR", "Prebuilt Lenovo Legion Core i7 RTX 4060 16GB RAM 1200 EUR"]

User: "budget running shoes for wide feet"
Output: ["New Balance Fresh Foam X 880v13 Wide EE", "Brooks Ghost 15 Wide 2E", "Asics Gel-Cumulus 25 Wide"]

### NOW ANALYZE THIS USER INPUT AND OUTPUT THE SPECIFICATION LIST:

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
        if response.tool_calls:
            call=response.tool_calls
            for i in call:
            
                if i['name']=="brave_search_tool":
            
                    web_result.append(ToolMessage(brave_search_tool.func(**i['args']),tool_call_id=i['id']))
        else:
            
            return llm_with_tools.invoke(web_result).content
        
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
def search_information(user_input:str)->dict:
    result=ast.literal_eval(extract_and_think(user_input=user_input))
    print(result)
    # for i in result:
    #     s=shopping_wrapper(i,max=2)
    #     for j in s:
    #         link=j['Link']
    #         webscrap(link)
    
search_information("my phone got stolen, new one under 100 euro")
        
