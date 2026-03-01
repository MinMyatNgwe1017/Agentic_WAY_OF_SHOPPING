from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import re
import time


"""
newbuy is not possible to webscrap

"""
def web_scrap(link):
    with sync_playwright() as p:
        # browser=p.firefox.launch(headless=True)
        browser = p.chromium.launch(headless=True)
        context=browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0")
        

        page=context.new_page()
        Stealth().apply_stealth_sync(page)    
        page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/" })
        page.goto(link)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1)
        image_url = "No image found"
        
        try:
            #general image
            image_url = page.locator('meta[property="og:image"]').get_attribute("content", timeout=1000)        
        except:
            try:
                
                #amazone image
                image_url = page.locator('#landingImage').get_attribute("src", timeout=1000) 
            except:
                try:
                    
                    #mark
                    image_url=page.locator('[data-testid="hero-image"]').get_attribute("src", timeout=1000)       
                except:
                        print("no Image found")
            
            
        product_name=""
        try:
            
            #general
            product_name = page.locator('meta[property="og:title"]').get_attribute("content", timeout=1000)  
            
        except:
            try:
                #amazon
                product_name = page.locator('span#productTitle').inner_text( timeout=1000)
            
            except:
                try:
                    #best_buy
                    product_name=page.locator('.h4').inner_text( timeout=1000)
                except Exception as e :
                    print("no found title")
                    print(e)
        
        browser.close()
        
        return {
            "image_url":image_url,
            "product_name":product_name,
            
        }
            
                     
            
        
            

        
        
                        
                        