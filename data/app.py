import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load the product data
script_dir = os.path.dirname(os.path.abspath(__file__))
products_file = os.path.join(script_dir, 'products.json')
with open(products_file, 'r') as json_file:
    products = json.load(json_file)

def generate_chatbot_response(query, product_data, memory=None):
    # Simple keyword-based responses for now
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! Welcome to Starky Shop. How can I help you today?"
    
    elif any(word in query_lower for word in ['product', 'item', 'what']):
        # Show some product information
        product_info = []
        for i, product in enumerate(product_data[:3]):  # Show first 3 products
            product_info.append(f"{i+1}. {product.get('title', 'N/A')} - ${product.get('variants', [{}])[0].get('price', 'N/A')}")
        
        return f"Here are some of our products:\n" + "\n".join(product_info)
    
    elif any(word in query_lower for word in ['price', 'cost', 'how much']):
        return "I can help you find product prices. Could you specify which product you're interested in?"
    
    elif any(word in query_lower for word in ['shipping', 'delivery']):
        return "Shipping information varies by product. Most items require shipping. Would you like to know about a specific product?"
    
    elif any(word in query_lower for word in ['bye', 'goodbye', 'exit']):
        return "Thank you for visiting Starky Shop! Have a great day!"
    
    else:
        return "I'm here to help with product information, pricing, and shipping questions. What would you like to know?"

# Flask API setup
app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('message', '') if data else ''
    if not user_query:
        return jsonify({'error': 'No message provided'}), 400
    answer = generate_chatbot_response(user_query, products)
    return jsonify({'response': answer})

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
