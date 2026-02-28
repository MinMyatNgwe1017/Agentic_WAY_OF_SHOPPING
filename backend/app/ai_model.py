
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
from typing import List
import os 
import dotenv

dotenv.load_dotenv("../../.env")

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

@tool 
def search_link(query:str,max:int)->List:
    
    """
    use this one to get the link of the the query
    it search on the internet and return the list of the link
    
    param:
    query:str:the one that you want to search on internet and also want to get link
    max:int:the number of query return that you want from internet along with link of the pages
    """
    with DDGS() as ddgs:
        results=list(ddgs.text(query,max_results=max))
    if len(results)<0:
        return "No result found"
    formatted_output = []
    for index, res in enumerate(results, 1):
        formatted_output.append(
            {"Result":index,"Title":res.get('title'),"Link":res.get('href')}
        )        
        
    time.sleep(0.1)
    return formatted_output

tools=[brave_search_tool,search_link,ask_user,retrun_not_possible]  
model=ChatOllama(model="qwen3.5:35b",temperature=0,base_url="127.0.0.1:11434")


extract_system_prompt="""
You are an expert product analyst and hardware specialist equipped with research and communication tools. Your job is to analyze a user's shopping request, determine their budget and use-case, deduce the best specific products that fit their needs, and rank them from best to worst.

CRITICAL: If the user's request lacks necessary details (like budget or specific use-case), you MUST ask for ALL missing information in a SINGLE question using the `ask_user` tool. Do not ask piece by piece. Only ask again if the user ignores a part of your question.
CRITICAL FOR MODEL: You are strictly forbidden from conversing directly with the user or asking questions in regular text. If you need more information, you MUST trigger the `ask_user` tool. If your response is just standard text ending in a question mark, you have failed your instructions.

### TOOL USAGE RULES:
You have access to tools. Use them appropriately before giving your final answer. You may use multiple tools in sequence, or use the same tool multiple times:
1. `ask_user`: Call this tool IF the request is far too vague to deduce anything. Ask for ALL missing critical info in one single question.
2. `retrun_not_possible`: Call this tool IF the user's request is completely unrealistic or factually impossible. Provide a clear reason why.
3. `brave_search_tool`: Call this tool IF you need to verify current market prices, availability, or the latest hardware models to build your ranked list.

### FINAL OUTPUT RULES (ONLY once you have all the information):
1. DYNAMIC NUMBER OF PRODUCTS: You MUST output as many highly relevant products as you can find that perfectly fit the user's criteria, up to a maximum of 10. Do not force a long list if only a few good options exist. Do not repeat the same product twice.
2. RANKING (CRITICAL): The list MUST be ordered from the absolute BEST recommendation (index 0) down to the lowest ranked recommendation. 
3. STRICT FORMATTING: Your final response MUST be ONLY a valid Python list of dictionaries. It must contain absolutely NO other data types, no markdown blocks, and no conversational filler. Just the raw list.
4. DICTIONARY SCHEMA: Each dictionary MUST have exactly three keys: "tag", "name", and "search_query".
   - "tag": A short, uppercase descriptor of why it was chosen (e.g., "BEST OVERALL", "BEST BATTERY", "BUDGET PICK"). Do not use brackets.
   - "name": The user-friendly display name containing the Brand, specific specs (CPU/RAM/GPU), and target price.
   - "search_query": The highly optimized string that a secondary agent will use to search the web for links. Include specific model numbers, crucial specs, and conditions (e.g., "Refurbished", "Used", "Open Box"). Do NOT include the price in this string, as it confuses search engines. 
   - NO NUMBERS: Do NOT include ranking numbers (like "1." or "2.") inside any strings. The ranking is implied by the order of the list.

### EXAMPLES OF HOW TO BEHAVE:

User: "laptop for student around 600eur"
[
  {{
    "tag": "BEST OVERALL",
    "name": "Lenovo IdeaPad Slim 3 AMD Ryzen 5 16GB RAM 512GB SSD 600 EUR",
    "search_query": "Lenovo IdeaPad Slim 3 AMD Ryzen 5 16GB RAM 512GB SSD laptop"
  }},
  {{
    "tag": "REFURBISHED DEAL",
    "name": "Apple MacBook Air M1 8GB RAM 256GB SSD 600 EUR",
    "search_query": "Apple MacBook Air M1 8GB 256GB refurbished used"
  }},
  {{
    "tag": "GAMING ON A BUDGET",
    "name": "Acer Nitro 5 FA506 RTX 3050 8GB RAM 700 EUR",
    "search_query": "Acer Nitro 5 FA506 RTX 3050 gaming laptop"
  }}
]

User: "I want a gaming pc for 50 bucks"
Action to take: Call the `retrun_not_possible` tool with the reason "50 bucks is not enough for a functioning gaming PC."

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
        if response.tool_calls:
            web_result.append(response)
            call=response.tool_calls
            for i in call:
            
                if i['name']=="brave_search_tool":
                    print("brave_search_is_called")
                    web_result.append(ToolMessage(brave_search_tool.func(**i['args']),tool_call_id=i['id']))
                    
                elif i['name']=="ask_user":

                    web_result.append(ToolMessage(ask_user.func(**i['args']),tool_call_id=i['id']))
                elif i['name']=="retrun_not_possible":
                    return retrun_not_possible.func(**i['args'])
        else:
            
            return llm_with_tools.invoke(web_result).content
        
        response=llm_with_tools.invoke(web_result)

second_agent_model=model.bind_tools([search_link])


agent2_system_prompt = """
You are a highly strict E-commerce Link Extractor. Your ONLY job is to take a specific product search query, use the `search_link` tool to find ready-to-buy links from ANY valid e-commerce store, and return exactly 3 pristine URLs.

CRITICAL INSTRUCTION: You MUST use the `search_link` tool. You are forbidden from hallucinating or making up URLs.

### ITERATION AND RETRYING (CRITICAL):
You can call the `search_link` tool AS MANY TIMES AS YOU WANT. 
If your first search returns junk, category pages, or no results, DO NOT GIVE UP. You MUST call the tool again with a modified search query. 
*Hint: If you get bad links, try appending words like "buy", "store", "amazon", "best buy", or "price" to your next search query to force better results.*

### LINK QUALITY CONTROL (UNIVERSAL RULES):
You must ONLY select URLs that point directly to a single, purchasable product page. You are strictly forbidden from using search results, category pages, lists, or review articles. 
Apply these universal heuristics to evaluate every link your tool finds:
1. REJECT SEARCH PAGES: Ignore any URL containing search parameters like `?q=`, `?k=`, `?keyword=`, `?search=`, or paths like `/search`, `/results`.
2. REJECT CATEGORY PAGES: Ignore any URL that points to a group of items (e.g., paths containing `/category/`, `/collections/`, `/c/`, `/catalog/`, `/shop/` or `/laptops/` without a specific product slug following it).
3. REJECT REVIEW SITES: Ignore URLs from tech blogs or review sites. If the URL contains words like "review", "best-laptops", "top-10", or "buying-guide", throw it away.
4. ACCEPT SPECIFIC ITEM PAGES: Look for highly specific URLs. Good URLs usually contain terms like `/product/`, `/item/`, `/p/`, `/dp/`, `/buy/`, or have a very long, specific slug at the end.

### OUTPUT FORMAT:
Your final response MUST be a valid Python dictionary containing exactly three keys: "link1", "link2", and "link3". 
Do NOT include the product name, do NOT include conversational text, and do NOT use markdown blocks. Just the raw dictionary.

Example Output:
{{
  "link1": "https://www.any-store.com/product/asus-rog-strix-18",
  "link2": "https://www.local-tech-shop.net/item/1928374",
  "link3": "https://www.another-store.com/dp/B08X..."
}}
"""
second_agent_prompttemplate=ChatPromptTemplate(
    [
        ("system",agent2_system_prompt),
        ("user","{user_input}")
    ]
)

second_agent=second_agent_prompttemplate|second_agent_model
def search_information(user_input:str)->dict:
    global second_agent
    number_of_link=2
    result=extract_and_think(user_input=user_input)
    try:
        result=ast.literal_eval(result)
        for i in result:            
            messages=[
                SystemMessage(agent2_system_prompt),
                HumanMessage(i['search_query'])]

            response=second_agent.invoke({"user_input":i["search_query"]})
            while response.tool_calls:
                messages.append(response)
                tool=response.tool_calls
                for j in tool:
                    if j['name']=="search_link":
                        print("search_link is called")
                        messages.append(ToolMessage(str(search_link.func(**j['args'])),tool_call_id=j['id']))
                response=second_agent_model.invoke(messages)
                
            final_reult=second_agent_model.invoke(messages)
            print(final_reult.content)                
        
    except Exception as e:
        print(f"An error occurred: {e}")

search_information("i want to buy laptop aroudn 1500eur gaming")
