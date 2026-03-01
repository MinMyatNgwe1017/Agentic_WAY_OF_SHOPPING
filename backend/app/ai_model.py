
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
from web_scraping import web_scrap
import json
from prompts import extract_system_prompt,agent2_system_prompt
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
                    return retrun_not_possible.func(**i['args']).content
        else:
            
            return llm_with_tools.invoke(web_result).content
        
        response=llm_with_tools.invoke(web_result)

second_agent_model=model.bind_tools([search_link])


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
                        print(j['args'])
                        messages.append(ToolMessage(str(search_link.func(**j['args'])),tool_call_id=j['id']))
                response=second_agent_model.invoke(messages)
                
            links=json.loads(response.content)
            
            print("done one",i,links)
            for i in links:
                result=web_scrap(links[i])
                print(i,result)
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    print(result)
    
search_information("Refurbished Apple MacBook Air M2 13 inch 8GB RAM 256GB SSD Silver")