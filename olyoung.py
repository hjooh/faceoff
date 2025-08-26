import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    url = 'https://global.oliveyoung.com/display/category?ctgrNo=1000000031'
    base_url = 'https://global.oliveyoung.com'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # part 1: pull page HTML with Playwright
        print(f"[*] Navigating to {url}...")
        await page.goto(url, wait_until='domcontentloaded')
        
        product_list_selector = "#categoryProductList"
        await page.wait_for_selector(f"{product_list_selector} li", timeout=15000)
        
        print("[+] Product list found! Extracting HTML...")
        product_list_html = await page.inner_html(product_list_selector)
        
        await browser.close()

    # part 2: parse pulled HTML with bs4
    print("[*] Parsing the extracted HTML...")
    soup = BeautifulSoup(product_list_html, 'html.parser')
    
    products = []
    
    product_items = soup.find_all('li', class_='prdt-unit')
    
    for item in product_items:
        # product name
        name_tag = item.find('img')
        name = name_tag['alt'].strip() if name_tag else 'N/A'
        
        # product url
        url_tag = item.find('a')
        product_url = base_url + url_tag['href'] if url_tag else 'N/A'
        
        # image
        image_url = name_tag['src'] if name_tag else 'N/A'
        
        # price
        current_price = 'N/A'
        original_price = 'N/A'
        
        price_info = item.find('div', class_='price-info')
        if price_info:
            # sale price exists
            sale_price_tag = price_info.find('strong', class_='point')
            original_price_tag = price_info.find('span')

            if sale_price_tag and original_price_tag:
                current_price = sale_price_tag.text.strip()
                original_price = original_price_tag.text.strip()
            # not on sale
            else:
                regular_price_tag = price_info.find('strong')
                if regular_price_tag:
                    current_price = regular_price_tag.text.strip()
                    original_price = current_price
        

        # brand
        brand_tag = item.select_one('dl.brand-info dt')
        brand = brand_tag.text.strip() if brand_tag else 'N/A'

        products.append({
            'name': name,
            'brand': brand,
            'current_price': current_price,
            'original_price': original_price, 
            'product_url': product_url,
            'image_url': image_url
        })
        
    print(f"\n[+] Success! Extracted data for {len(products)} products.")
    
    # Pretty-print the final list of products
    print(json.dumps(products, indent=2))


if __name__ == "__main__":
    asyncio.run(main())