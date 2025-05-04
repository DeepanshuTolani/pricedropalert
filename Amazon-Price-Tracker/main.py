import requests
from bs4 import BeautifulSoup
import pygame
import os
import time
import json
import random
from colored import fg, attr

print("Starting Amazon Price Tracker...")

# Load settings.json
try:
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    print("Settings loaded:", settings)
except Exception as e:
    print(f"Error loading settings.json: {e}")
    exit(1)

# Initialize pygame mixer
try:
    pygame.mixer.init()
    pygame.mixer.music.load(settings["remind-sound-path"])
    print("Pygame mixer initialized with sound:", settings["remind-sound-path"])
except Exception as e:
    print(f"Error initializing pygame or loading sound: {e}")
    exit(1)

# Set budget
my_price = settings['budget']
print(f"Budget set to: {my_price}")

# Currency symbols
currency_symbols = ['€', '£', '$', '¥', 'HK$', '₹']
print("Currency symbols:", currency_symbols)

# URL and headers
URL = settings['url']
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}
print(f"Fetching URL: {URL}")

# Create a session for persistent cookies
session = requests.Session()

# Check price function
def checking_price():
    print("Checking price...")
    try:
        # Random delay to avoid bot detection
        time.sleep(random.uniform(1, 5))
        # Fetch webpage
        print("Sending HTTP request...")
        page = session.get(URL, headers=headers, timeout=10)
        print(f"HTTP Status Code: {page.status_code}")
        if page.status_code != 200:
            print(f"Response text: {page.text[:500]}...")
        page.raise_for_status()
        print("Webpage fetched successfully")

        # Check for CAPTCHA
        if "captcha" in page.text.lower():
            print(f"CAPTCHA detected! Response snippet: {page.text[:1000]}...")
            print("Retrying in 60 seconds...")
            time.sleep(60)
            return

        # Parse webpage
        print("Parsing webpage...")
        soup = BeautifulSoup(page.text, 'html.parser')

        # Debug: Print HTML snippet
        print("Raw HTML snippet:", page.text[:1000])

        # Find product title with multiple selectors
        title_selectors = [
            ('span', {'id': 'productTitle'}),
            ('h1', {'id': 'title'}),
            ('span', {'class': 'a-size-large product-title'}),
        ]

        product_title = None
        for tag, attrs in title_selectors:
            element = soup.find(tag, attrs)
            if element:
                product_title = element.getText().strip()
                print(f"Found title with {tag} {attrs}: {product_title}")
                break
        else:
            print("Product title not found with any selector!")
            all_titles = soup.find_all(['span', 'h1'], id=['productTitle', 'title'])
            print("All potential title elements:", [el.getText().strip() for el in all_titles])
            return

        # Try multiple price selectors
        price_selectors = [
            ('span', {'class': 'a-price-whole'}),
            ('span', {'class': 'a-offscreen'}),
            ('span', {'class': 'a-price'}),
        ]

        product_price = None
        for tag, attrs in price_selectors:
            element = soup.find(tag, attrs)
            if element:
                product_price = element.getText()
                print(f"Found price with {tag} {attrs}: {product_price}")
                break
        else:
            print("Price element not found with any selector!")
            all_offscreen = soup.find_all('span', class_='a-offscreen')
            print("All a-offscreen elements:", [el.getText() for el in all_offscreen])
            return

        # Remove currency symbols
        for i in currency_symbols:
            product_price = product_price.replace(i, '')

        # Convert to integer
        try:
            product_price = int(float(product_price.strip().replace(',', '')))
        except ValueError as e:
            print(f"Error converting price '{product_price}' to number: {e}")
            return

        # Print results
        print(f"{fg('green_1')}The Product Name is:{attr('reset')}{fg('dark_slate_gray_2')} {product_title}{attr('reset')}")
        print(f"{fg('green_1')}The Price is:{attr('reset')}{fg('orange_red_1')} {product_price}{attr('reset')}")

        # Check if price is within budget
        if product_price < my_price:
            print(f"{fg('medium_orchid_1b')}You Can Buy This Now!{attr('reset')}")
            try:
                pygame.mixer.music.play()
                time.sleep(3)
            except Exception as e:
                print(f"Error playing sound: {e}")
            # exit()  # Uncomment after debugging
        else:
            print(f"{fg('red_1')}The Price Is Too High!{attr('reset')}")

    except Exception as e:
        print(f"Unexpected error in checking_price: {e}")
        import traceback
        traceback.print_exc()

# Main loop
while True:
    try:
        checking_price()
        print(f"Sleeping for {settings['remind-time']} seconds...")
        time.sleep(settings['remind-time'])
    except KeyboardInterrupt:
        print("Script interrupted by user")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(10)