import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SHOP_NAME = os.environ.get("SHOP_NAME")
ACCESS_TOKEN = os.environ.get("SHOPIFY_API_KEY")  # Using your preferred variable name

if not SHOP_NAME or not ACCESS_TOKEN:
    raise Exception("SHOP_NAME or SHOPIFY_API_KEY not set in .env")

# Shopify API endpoint for products
url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2024-01/products.json?limit=250"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

all_products = []
page = 1

while True:
    print(f"Fetching page {page}...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error fetching products:", response.text)
        break
    data = response.json().get("products", [])
    if not data:
        break
    all_products.extend(data)
    # Shopify REST API pagination: check for 'Link' header for next page
    link = response.headers.get("Link")
    if link and 'rel="next"' in link:
        # Extract next page URL from Link header
        next_url = link.split(";")[0].strip("<> ")
        url = next_url
        page += 1
    else:
        break

# Save to products.json
os.makedirs("data", exist_ok=True)
with open("data/products.json", "w") as f:
    json.dump(all_products, f, indent=2)

print(f"Synced {len(all_products)} products to data/products.json")
