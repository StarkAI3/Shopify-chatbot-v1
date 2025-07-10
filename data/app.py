import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import markdown
from dotenv import load_dotenv

load_dotenv()

# Load the product data
script_dir = os.path.dirname(os.path.abspath(__file__))
products_file = os.path.join(script_dir, 'products.json')
with open(products_file, 'r') as json_file:
    products = json.load(json_file)

SHOP_NAME = "mffws4-kk"
SHOP_URL = f"https://{SHOP_NAME}.myshopify.com"

HELICONE_API_KEY = os.environ.get("HELICONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def call_gemini_via_helicone(prompt):
    url = "https://gateway.helicone.ai/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GOOGLE_API_KEY}",
        "helicone-auth": f"Bearer {HELICONE_API_KEY}",
        "helicone-target-url": "https://generativelanguage.googleapis.com"
    }
    data = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "Sorry, I couldn't get a response from Gemini."

def find_product_by_name(query, product_data):
    query_lower = query.lower()
    matching_products = []
    stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'link', 'url', 'buy', 'purchase', 'provide', 'give', 'me', 'please', 'can', 'you']
    words = query_lower.split()
    search_terms = [word for word in words if word not in stop_words and len(word) > 2]
    for product in product_data:
        title_lower = product.get('title', '').lower()
        for term in search_terms:
            if term in title_lower:
                matching_products.append(product)
                break
    return matching_products

def generate_product_link(product):
    handle = product.get('handle', '')
    if handle:
        return f"{SHOP_URL}/products/{handle}"
    return None

def generate_chatbot_response(query, product_data, memory=None):
    query_lower = query.lower()
    if any(word in query_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! Welcome to Starky Shop. How can I help you today?"
    elif any(word in query_lower for word in ['product', 'item', 'what']):
        product_info = []
        for i, product in enumerate(product_data[:3]):
            title = product.get('title', 'N/A')
            price = product.get('variants', [{}])[0].get('price', 'N/A')
            link = generate_product_link(product)
            if link:
                product_info.append(f"{i+1}. [{title}]({link}) - ${price}")
            else:
                product_info.append(f"{i+1}. {title} - ${price}")
        return f"Here are some of our products:\n" + "\n".join(product_info)
    elif any(word in query_lower for word in ['price', 'cost', 'how much']):
        return "I can help you find product prices. Could you specify which product you're interested in?"
    elif any(word in query_lower for word in ['shipping', 'delivery']):
        return "Shipping information varies by product. Most items require shipping. Would you like to know about a specific product?"
    elif any(word in query_lower for word in ['link', 'url', 'buy', 'purchase']):
        search_terms = query_lower.replace('link', '').replace('url', '').replace('buy', '').replace('purchase', '').strip()
        if search_terms:
            matching_products = find_product_by_name(search_terms, product_data)
            if matching_products:
                response = "Here are the products I found:\n"
                for i, product in enumerate(matching_products[:5]):
                    title = product.get('title', 'N/A')
                    price = product.get('variants', [{}])[0].get('price', 'N/A')
                    link = generate_product_link(product)
                    if link:
                        response += f"{i+1}. [{title}]({link}) - ${price}\n"
                    else:
                        response += f"{i+1}. {title} - ${price}\n"
                return response
            else:
                return f"I couldn't find any products matching '{search_terms}'. Try searching for a different product name."
        else:
            return "Please specify which product you'd like the link for. For example: 'link for belts' or 'buy t-shirt'"
    elif any(word in query_lower for word in ['bye', 'goodbye', 'exit']):
        return "Thank you for visiting Starky Shop! Have a great day!"
    else:
        matching_products = find_product_by_name(query, product_data)
        if matching_products:
            response = f"I found some products that might interest you:\n"
            for i, product in enumerate(matching_products[:3]):
                title = product.get('title', 'N/A')
                price = product.get('variants', [{}])[0].get('price', 'N/A')
                link = generate_product_link(product)
                if link:
                    response += f"{i+1}. [{title}]({link}) - ${price}\n"
                else:
                    response += f"{i+1}. {title} - ${price}\n"
            response += "You can ask me for product links, prices, or shipping information!"
            return response
        else:
            # Fallback: ask Gemini for a general answer
            return call_gemini_via_helicone(query)

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('message', '') if data else ''
    if not user_query:
        return jsonify({'error': 'No message provided'}), 400
    answer = generate_chatbot_response(user_query, products)
    html_answer = markdown.markdown(answer)
    return jsonify({'response': html_answer})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'api':
        app.run(host="0.0.0.0", port=5000)
    else:
        print("Welcome to Starky Shop Chatbot! Type 'quit' to exit.\n")
        while True:
            user_query = input("You: ").strip()
            if user_query.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            answer = generate_chatbot_response(user_query, products)
            print(f"Bot: {answer}\n")
