from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import re
import time


def extract_price(page):
    # 1. Try metadata first
    meta_selectors = [
        'meta[property="product:price:amount"]',
        'meta[itemprop="price"]',
        'meta[property="og:price:amount"]',
    ]

    for selector in meta_selectors:
        try:
            value = page.locator(selector).get_attribute("content", timeout=1000)
            if value:
                return value.strip()
        except:
            pass

    # 2. Try common product price selectors
    price_selectors = [
        '[data-testid="customer-price"]',
        '[data-testid="price"]',
        '.priceView-customer-price span',
        '.priceView-hero-price span',
        '.pricing-price__sale-price',
        '.a-price .a-offscreen',   # Amazon
    ]

    for selector in price_selectors:
        try:
            text = page.locator(selector).first.inner_text(timeout=1500)
            match = re.search(r"\$?\s?\d[\d,]*(?:\.\d{2})?", text)
            if match:
                return match.group(0).strip()
        except:
            pass

    # 3. Last fallback: search whole page text for price
    try:
        body_text = page.locator("body").inner_text(timeout=2000)
        matches = re.findall(r"\$\s?\d[\d,]*(?:\.\d{2})?", body_text)
        if matches:
            return matches[0].strip()
    except:
        pass

    return None


def web_scrap(link):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )

        page = context.new_page()
        Stealth().apply_stealth_sync(page)

        page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        })

        image_url = None
        product_name = None
        price = None

        try:
            page.goto(link, timeout=15000, wait_until="domcontentloaded")
            time.sleep(2)

            try:
                image_url = page.locator('meta[property="og:image"]').get_attribute("content", timeout=1000)
            except:
                try:
                    image_url = page.locator("#landingImage").get_attribute("src", timeout=1000)
                except:
                    try:
                        image_url = page.locator('[data-testid="hero-image"]').get_attribute("src", timeout=1000)
                    except:
                        try:
                            image_url = page.locator(".primary-image").get_attribute("src", timeout=1000)
                        except:
                            print("No image found")

            try:
                product_name = page.locator('meta[property="og:title"]').get_attribute("content", timeout=1000)
            except:
                try:
                    product_name = page.locator("span#productTitle").inner_text(timeout=1000)
                except:
                    try:
                        product_name = page.locator(".h4").inner_text(timeout=1000)
                    except Exception as e:
                        print("No title found")
                        print(e)

            price = extract_price(page)

            return {
                "image_url": image_url,
                "product_name": product_name,
                "link": link,
                "price": price
            }

        except Exception as e:
            print(e)

            return {
                "image_url": image_url,
                "product_name": product_name,
                "link": link,
                "price": price,
            }

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    print(
        web_scrap(
            "https://www.bestbuy.com/product/gtplayer-gaming-chair-with-rgb-led-lights-breathable-fabric-ergonomic-high-back-computer-chair-rgb-black/JXTR69YG4X"
        )
    )