from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import re
import time

def scrape_product_details(url: str) -> str:
    """
    Scrapes a product page for its name, price, and image.
    Use this when you have a specific store link and need to confirm the deal.
    """
    # Safety: Handle if LLM passes a dict instead of string
    target_url = url.get("url", url.get("value", str(url))) if isinstance(url, dict) else str(url)
    
    print(f"\n[Agent Scraper] Analyzing: {target_url}...")
    
    with sync_playwright() as p:
        # We use Firefox because it bypassed the Acer firewall
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        )
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        
        try:
            page.goto(target_url, wait_until="load", timeout=30000)
            time.sleep(2) # Allow dynamic prices to render
            
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # 1. Extract Info
            og_title = soup.find("meta", property="og:title")
            title = og_title["content"] if og_title else (soup.title.string if soup.title else "Unknown")
            
            og_image = soup.find("meta", property="og:image")
            image = og_image["content"] if og_image else "No Image Found"
            
            # Price detection (Meta tags + common CSS classes)
            og_price = soup.find("meta", property="product:price:amount") or soup.find("meta", property="og:price:amount")
            price = og_price["content"] if og_price else "Check Page Text"

            # 2. Clean Text for LLM reasoning
            for junk in soup(["script", "style", "nav", "footer", "header"]):
                junk.extract()
            text = soup.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text)[:2000] # Limit to 2000 chars

            return (
                f"SOURCE: {target_url}\n"
                f"PRODUCT NAME: {title}\n"
                f"IMAGE: {image}\n"
                f"METADATA PRICE: {price}\n"
                f"PAGE CONTENT: {text}"
            )
            
        except Exception as e:
            return f"FAILED: Could not read {target_url}. Error: {str(e)}"
        finally:
            browser.close()
            
# 1. Run the scraper
result = scrape_product_details("https://store.acer.com/fi-fi/acer-nitro-v-15-pelikannettava-anv15-51-musta-nh-qnbed-8")

# 2. Extract using the EXACT labels from your return string
# Note: Added safety check to prevent crash if scraping failed
if "FAILED" not in result:
    try:
        # Match "IMAGE: " instead of "Image: "
        image_url = result.split("IMAGE: ")[1].split("\n")[0]
        # Match "PRODUCT NAME: " instead of "Name: "
        product_name = result.split("PRODUCT NAME: ")[1].split("\n")[0]
        # Match "METADATA PRICE: " instead of "Price Tags: "
        price = result.split("METADATA PRICE: ")[1].split("\n")[0]

        # 3. Create the HTML file
        html_template = f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; display: inline-block;">
                    <h1>{product_name}</h1>
                    <img src="{image_url}" width="400" style="border-radius: 5px;">
                    <h2 style="color: #2ecc71;">Price: {price}€</h2>
                    <p style="color: #666;">Scraped from Acer Official Store</p>
                </div>
            </body>
        </html>
        """
        with open("report.html", "w", encoding="utf-8") as f:
            f.write(html_template)

        print("\n✅ Report generated! Open 'report.html' in your folder to see the image.")
    except IndexError:
        print("\n❌ Error: Could not parse the scraped results. Check your split labels.")
else:
    print(f"\n❌ Scraper failed: {result}")