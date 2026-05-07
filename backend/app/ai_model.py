import subprocess
import time
import os
import dotenv
import json
import requests
from typing import List
import numpy as np

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.tools import tool
from langchain.agents import create_agent
import ast
from ddgs import DDGS
from bs4 import BeautifulSoup
import cloudscraper
from web_scraping import web_scrap
from prompts import extract_system_prompt, agent2_system_prompt,recommendation_prompt
from sqlalchemy import create_engine
from ai_tools import brave_search_tool,ask_user,retrun_not_possible,search_link
import os 
dotenv.load_dotenv("../../.env")

from pathlib import Path
from sqlalchemy import create_engine

from concurrent.futures import ThreadPoolExecutor, as_completed

db_path = os.path.expanduser("~/chat_memory.db")
db_url = f"sqlite:///{db_path}"

engine = create_engine(db_url, connect_args={"check_same_thread": False})

def safe_parse(text):
    """
    Parse LLM output safely.
    Handles JSON, python lists, code fences, and extra text around the list/dict.
    """
    if text is None:
        raise ValueError("LLM output empty")

    t = text.strip()
    
    t = t.replace("{{", "{").replace("}}", "}")
    if t.startswith("```"):
        t = t.strip("`")
        if "\n" in t:
            t = t.split("\n", 1)[1].strip()

    try:
        return json.loads(t)
    except:
        pass

    try:
        return ast.literal_eval(t)
    except:
        pass

    # try extracting first list
    start_list = t.find("[")
    end_list = t.rfind("]")
    if start_list != -1 and end_list != -1 and end_list > start_list:
        candidate = t[start_list:end_list + 1]
        try:
            return json.loads(candidate)
        except:
            pass
        try:
            return ast.literal_eval(candidate)
        except:
            pass

    # try extracting first dict
    start_dict = t.find("{")
    end_dict = t.rfind("}")
    if start_dict != -1 and end_dict != -1 and end_dict > start_dict:
        candidate = t[start_dict:end_dict + 1]
        try:
            return json.loads(candidate)
        except:
            pass
        try:
            return ast.literal_eval(candidate)
        except:
            pass

    raise ValueError(f"Cannot parse LLM output: {t[:300]}")



tools = [brave_search_tool, ask_user, retrun_not_possible]

model = ChatOllama(model="qwen3.5:9b", temperature=0, base_url="http://127.0.0.1:11434")

llm_with_tools = model.bind_tools(tools)

extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", extract_system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}")
    ]
)
extract_chain = extract_prompt | llm_with_tools


def get_session_history(session_id: int):
    return SQLChatMessageHistory(
        session_id=str(session_id),
        connection=engine,
        table_name="message_history"
    )


agent_1 = RunnableWithMessageHistory(
    runnable=extract_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)



second_agent_model = model.bind_tools([search_link, brave_search_tool])

second_agent_prompttemplate = ChatPromptTemplate(
    [
        ("system", agent2_system_prompt),
        ("user", "{user_input}")
    ]
)

thrid_agent_template=ChatPromptTemplate(
    [
        ("system",recommendation_prompt),
        MessagesPlaceholder("web_search")
    ]
)

second_agent = second_agent_prompttemplate | second_agent_model

thrid_agent_model=model.bind_tools([search_link])

third_agent=thrid_agent_template|thrid_agent_model

def stream_products(user_input, session_id):

    global agent_1, llm_with_tools,third_agent

    history = get_session_history(session_id)

    web_result = []

    web_result.append(SystemMessage(extract_system_prompt))
    web_result.extend(history.messages)
    web_result.append(HumanMessage(user_input))

    # added: initial live status
    yield {
        "type": "status",
        "message": "Analyzing your request..."
    }
    print("before running")

    response = agent_1.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    print("after running",response)

    while True:
        if response.tool_calls:
            web_result.append(response)
            call = response.tool_calls

            for i in call:
                tool_args = i["args"]
                print("STREAM TOOL CALL:", i["name"], tool_args)

                if i["name"] == "brave_search_tool":
                    # added: stream live search log
                    yield {
                        "type": "status",
                        "message": f"Searching: {tool_args.get('search_query', '')}"
                    }

                    web_result.append(

                        ToolMessage(
                            
                            brave_search_tool.func(**i["args"]),
                            tool_call_id=i["id"]
                        
                        )
                    )


                elif i["name"] == "ask_user":
                    actual_question = i["args"]["question"]
                    yield {
                        "status": "need_user",
                        "question": actual_question
                    }
                    return

                elif i["name"] == "retrun_not_possible":
                    yield {
                        "status": "not_possible",
                        "reason": retrun_not_possible.func(**i["args"])
                    }
                    return

            response = llm_with_tools.invoke(web_result)

        else:
            llm_response = response.content
            

            history.add_message(AIMessage(llm_response))

            print("RAW STREAM LLM RESPONSE:", repr(llm_response))
            break


    try:
        queries = safe_parse(llm_response)

    except Exception as e:
        yield {
            "error": str(e),
            "raw_output": llm_response
        }
        return

    # added: status after parsing candidate products
    yield {
        "type": "status",
        "message": f"Found {len(queries)} products, checking stores and details..."
    }

    def process_product(product):

        try:
            messages = [
                SystemMessage(agent2_system_prompt),
                HumanMessage(product["search_query"])
            ]

            response = second_agent.invoke({"user_input": product["search_query"]})

            while response.tool_calls:
                messages.append(response)
                tool_calls = response.tool_calls

                for j in tool_calls:
                    tool_name = j["name"]
                    tool_args = j["args"]
                    tool_id = j["id"]

                    try:
                        if tool_name == "search_link":
                            print(f"Agent 2 searching links: {tool_args}")
                            tool_result = str(search_link.func(**tool_args))

                        elif tool_name == "brave_search_tool":
                            print(f"Agent 2 researching: {tool_args}")
                            tool_result = str(brave_search_tool.func(**tool_args))

                        else:
                            tool_result = "Unsupported tool"

                        if not tool_result or tool_result.strip() == "":
                            tool_result = "Error: No results found."

                    except Exception as e:
                        print(f"Tool {tool_name} failed: {e}")
                        tool_result = f"Search failed: {e}"

                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tool_id)
                    )

                response = second_agent.invoke(messages)

            print("RAW SECOND AGENT RESPONSE:", repr(response.content))

            links = safe_parse(response.content)

            for i in links:
                scraped = web_scrap(links[i])

                if None in list(scraped.values()):
                    continue

                return scraped

        except Exception as e:
            return {"error": str(e)}

    with ThreadPoolExecutor(max_workers=4) as executor:

        # added: log each product being checked
        futures = []
        for p in queries:
            yield {
                "type": "status",
                "message": f"Checking product: {p.get('name', p.get('search_query', 'Unknown product'))}"
            }
            futures.append(executor.submit(process_product, p))

        for future in as_completed(futures):

            result = future.result()

            if result:
                searching_result=[]

                third_agent_response=third_agent.invoke(
                    {"userinput":history.messages,"product_info":result,"web_search":searching_result}
                )
                while third_agent_response.tool_calls:
                    searching_result.append(third_agent_response)
                    for i in  third_agent_response.tool_calls:
                        
                        if i['name']=="brave_search_tool":
                            searching_result.append(
                                ToolMessage(
                                    brave_search_tool.func(**i['args'],
                                                           tool_call_id=i['id'])
                                )
                            )

                    third_agent_response=third_agent.invoke(
                        {"userinput":history.messages,"product_info":result,"history":searching_result}
                    )
                    
                result['recom']=third_agent_response.content
                print(result)
                    
                    
                
                yield result
    print("STREAM PRODUCTS FINISHED")


import asyncio
if __name__ == "__main__":
    for i in stream_products("give me secondhand phone around 100eur", 10):
        print(i)

    # model=ChatOllama(model="qwen3.5:35b",temperature=0,base_url="http://127.0.0.1:11434")

    # print(model.invoke("hello"))
# search_information("bmw 330Emsport steering wheel")