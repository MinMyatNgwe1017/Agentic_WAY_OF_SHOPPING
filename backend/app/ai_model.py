import subprocess
import time 
import os 
import dotenv
import json
import requests
from typing import List
import numpy as np

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
from bs4 import BeautifulSoup
import cloudscraper
from web_scraping import web_scrap
from prompts import extract_system_prompt,agent2_system_prompt
from sqlalchemy import create_engine 
dotenv.load_dotenv("../../.env")

import os
from sqlalchemy import create_engine

db_path = "/home/user/conversation.db"
db_url = f"sqlite:///{db_path}"

engine = create_engine(db_url, connect_args={"check_same_thread": False})
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
    

    return question

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

model=ChatOllama(model="qwen3.5:35b",temperature=0,base_url="http://127.0.0.1:11434")

llm_with_tools=model.bind_tools(tools)

extract_prompt=ChatPromptTemplate.from_messages(
    [
        ("system",extract_system_prompt),
        MessagesPlaceholder("history"),
        ("human","{input}")
    ]
)
extract_chain=extract_prompt|llm_with_tools



def get_session_history(session_id:int):
    return SQLChatMessageHistory(
        session_id=str(session_id),
        connection=engine,
        table_name="message_history"
    )
    
        
agent_1=RunnableWithMessageHistory(
    runnable=extract_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

def extract_and_think(user_input,session_id):
    global agent_1,llm_with_tools,extract_system_prompt,extract_chain
    web_result=[]
    history=get_session_history(session_id)
    
    
    web_result.append(SystemMessage(extract_system_prompt))
    web_result.extend(history.messages)
    web_result.append(HumanMessage(user_input))
    print("engter the function")
    
    
    response=agent_1.invoke({"input":user_input},config={"configurable":{"session_id":session_id}})
    print(response)
    while True:
        if response.tool_calls:
            web_result.append(response)
            call=response.tool_calls
            for i in call:

                tool_args=i['args']
                print(tool_args)

                if i['name']=="brave_search_tool":
                    
                    print("Duck Duck go search is called")

                    web_result.append(ToolMessage(brave_search_tool.func(**i['args']),tool_call_id=i['id']))
                    
                elif i['name']=="ask_user":
                    print("yest it work")
                    actual_question = i['args']['question']
                    tool_msg = ToolMessage(
                        
                        content=actual_question,
                    
                        tool_call_id=i["id"]
                    )
                    history.add_message(tool_msg)     
                    return "asking user input"
                elif i['name']=="retrun_not_possible":
                    return retrun_not_possible.func(**i['args'])
                
            response=llm_with_tools.invoke(web_result)
        else:
            llm_response=llm_with_tools.invoke(web_result).content
            
            history.add_message(AIMessage(llm_response))
            return search_information(llm_response)
        


second_agent_model=model.bind_tools([search_link,brave_search_tool])

second_agent_prompttemplate=ChatPromptTemplate(
    [
        ("system",agent2_system_prompt),
        ("user","{user_input}")
    ]
)


second_agent=second_agent_prompttemplate|second_agent_model


def search_information(llm_response:str)->dict:
    global second_agent
    result=llm_response
    try:
        result=ast.literal_eval(result)

        for i in result:            
            messages=[
                SystemMessage(agent2_system_prompt),
                HumanMessage(i['search_query'])]

            response=second_agent.invoke({"user_input":i["search_query"]})
            while response.tool_calls:
                messages.append(response)
                tool = response.tool_calls
                
                for j in tool:
                    tool_name = j['name']
                    tool_args = j['args']
                    tool_id = j['id']
                    
                    try: 
                        if tool_name == "search_link":
                            
                            print(f" Agent 2 searching links: {tool_args}")
                            tool_result = str(search_link.func(**tool_args))
                            
                        elif tool_name == "brave_search_tool":
                            print(f"Agent 2 researching: {tool_args}")

                            tool_result = str(brave_search_tool.func(**tool_args))
                        
                        if not tool_result or tool_result.strip() == "":
                            tool_result = "Error: No results found. Modify your query and try again."
                            
                    except Exception as e:
                        print(f"Tool {tool_name} failed: {e}")
                        tool_result = f"Search failed: {e}. Do not use these exact keywords again. Try a different store or broader terms."
                    
                    messages.append(ToolMessage(content=tool_result, tool_call_id=tool_id))
                
                response = second_agent.invoke(messages)            
            
            links=json.loads(response.content)
        
            print("done one",i,links)
            for i in links:
                result=web_scrap(links[i])
                if None in list(result.values()):
                    print(result)

                    continue
                else:
                    print(i,result)
                    break
                    
    except Exception as e:
        print(f"An error occurred: {e}")
    print(result)


import asyncio
if __name__=="__main__":
        print(extract_and_think("buget gamming headphone around 50eur",50))
    
    # model=ChatOllama(model="qwen3.5:35b",temperature=0,base_url="http://127.0.0.1:11434")

    # print(model.invoke("hello"))
# search_information("bmw 330Emsport steering wheel")
