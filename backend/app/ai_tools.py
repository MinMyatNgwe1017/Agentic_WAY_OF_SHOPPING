from ddgs import DDGS
from langchain_core.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
from typing import List
import time 
@tool
def brave_search_tool(search_query: str, max_query) -> str:
    """Searches the web for products and returns results
        param:
        search_query:str ->the thing that you want to search on internet
        max_query:int ->what is the number of query you want to return more query more information less query number less information
    """

    message = search_query
    if isinstance(message, dict):
        if "value" in message:
            message = message['value']

    search = DuckDuckGoSearchRun(wrapper=DuckDuckGoSearchAPIWrapper(max_results=max_query))
    result = search.invoke(message)
    print(len(result))
    return result


@tool
def ask_user(question: str) -> str:
    """
    use this if u think the user information is not enough

    param:
    question:str

    """

    return question


@tool
def retrun_not_possible(reason: str) -> str:
    """
    call this function based on the the information that user ask does not found for
    eg find the iphone around 10eur not possible thing return the reason

    param:
    reason:str
    """
    return reason


@tool
def search_link(query: str, max: int) -> List:

    """
    use this one to get the link of the the query
    it search on the internet and return the list of the link

    param:
    query:str:the one that you want to search on internet and also want to get link
    max:int:the number of query return that you want from internet along with link of the pages
    """
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max))
    if len(results) < 0:
        return "No result found"
    formatted_output = []
    for index, res in enumerate(results, 1):
        formatted_output.append(
            {"Result": index, "Title": res.get('title'), "Link": res.get('href')}
        )

    time.sleep(0.1)

    return formatted_output
