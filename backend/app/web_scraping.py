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
<<<<<<< HEAD
        browser=p.firefox.launch(headless=True)
        # browser = p.chromium.launch(headless=True)
        context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            )        

        page=context.new_page()
        Stealth().apply_stealth_sync(page)    
        page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/" })
        image_url = None
        product_name=None


        try:
            page.goto(link)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1)
            
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
                        
                        try:
                            #best_buy
                            image_url=page.locator('.primary-image').get_attribute("src", timeout=1000)    
                        except:                       
                            print("no Image found")
                
            
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
        except Exception as e:
            print(e)
            return {
                "image_url":image_url,
                "product_name":product_name,
                
            }

                
                            
if __name__=="__main__":
    print(web_scrap(r"https://www.bestbuy.com/product/gtplayer-gaming-chair-with-rgb-led-lights-breathable-fabric-ergonomic-high-back-computer-chair-rgb-black/JXTR69YG4X"))
                        
                        
=======
        # browser=p.firefox.launch(headless=True)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        )

        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        page.set_extra_http_headers(
            {"Accept-Language": "en-US,en;q=0.9", "Referer": "https://www.google.com/"}
        )
        page.goto(link)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1)
        image_url = "No image found"

        try:
            # general image
            image_url = page.locator('meta[property="og:image"]').get_attribute(
                "content", timeout=1000
            )
        except:
            try:

                # amazone image
                image_url = page.locator("#landingImage").get_attribute(
                    "src", timeout=1000
                )
            except:
                try:

                    # mark
                    image_url = page.locator(
                        '[data-testid="hero-image"]'
                    ).get_attribute("src", timeout=1000)
                except:
                    print("no Image found")

        product_name = ""
        try:

            # general
            product_name = page.locator('meta[property="og:title"]').get_attribute(
                "content", timeout=1000
            )

        except:
            try:
                # amazon
                product_name = page.locator("span#productTitle").inner_text(
                    timeout=1000
                )

            except:
                try:
                    # best_buy
                    product_name = page.locator(".h4").inner_text(timeout=1000)
                except Exception as e:
                    print("no found title")
                    print(e)

        browser.close()

        return {
            "image_url": image_url,
            "product_name": product_name,
        }
>>>>>>> 06cb464f8e810f58f03391311ef9069d81897c68
