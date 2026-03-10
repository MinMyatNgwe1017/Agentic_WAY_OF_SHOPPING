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
from prompts import extract_system_prompt, agent2_system_prompt
from sqlalchemy import create_engine
dotenv.load_dotenv("../../.env")

import os
from sqlalchemy import create_engine

from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_and_think(user_input, session_id):
    global agent_1, llm_with_tools, extract_system_prompt, extract_chain
    web_result = []
    history = get_session_history(session_id)

    web_result.append(SystemMessage(extract_system_prompt))
    web_result.extend(history.messages)
    web_result.append(HumanMessage(user_input))
    print("enter the function")

    response = agent_1.invoke({"input": user_input}, config={"configurable": {"session_id": session_id}})
    print(response)
    while True:
        if response.tool_calls:
            web_result.append(response)
            call = response.tool_calls
            for i in call:

                tool_args = i['args']
                print(tool_args)

                if i['name'] == "brave_search_tool":

                    print("Duck Duck go search is called")

                    web_result.append(ToolMessage(brave_search_tool.func(**i['args']), tool_call_id=i['id']))

                elif i['name'] == "ask_user":
                    actual_question = i['args']['question']
                    tool_msg = ToolMessage(

                        content=actual_question,

                        tool_call_id=i["id"]
                    )
                    history.add_message(tool_msg)
                    return "asking user input"
                elif i['name'] == "retrun_not_possible":
                    return retrun_not_possible.func(**i['args'])

            response = llm_with_tools.invoke(web_result)
        else:
            llm_response=llm_with_tools.invoke(web_result).content
            
            history.add_message(AIMessage(llm_response))

            # retuning list of product
            products = search_information(llm_response)

            return {
                "session_id": session_id,
                "query": user_input,
                "products": products["products"]
            }

def search_information(llm_response: str) -> dict:
    global second_agent
    result = llm_response

    products = []

    try:
        result = safe_parse(result)

        def process_product(product):

            messages = [
                SystemMessage(agent2_system_prompt),
                HumanMessage(product['search_query'])
            ]

            response = second_agent.invoke({"user_input": product["search_query"]})

            while response.tool_calls:

                messages.append(response)
                tool = response.tool_calls

                for j in tool:

                    tool_name = j['name']
                    tool_args = j['args']
                    tool_id = j['id']

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

                    print(scraped)

                    continue

                else:

                    print(i, scraped)

                    return scraped

        # Parallel exec
        with ThreadPoolExecutor(max_workers=4) as executor:

            futures = [executor.submit(process_product, p) for p in result]

            for future in as_completed(futures):

                item = future.result()

                if item:
                    products.append(item)

    except Exception as e:

        print(f"An error occurred: {e}")

    return {
        "products": products
    }


