import os
import json
import requests
import time
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import markdown
from dotenv import load_dotenv
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helicone_config import HeliconeConfig, get_helicone_headers, get_request_data

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the product data
script_dir = os.path.dirname(os.path.abspath(__file__))
products_file = os.path.join(script_dir, 'products.json')
with open(products_file, 'r') as json_file:
    products = json.load(json_file)

SHOP_NAME = "mffws4-kk"
SHOP_URL = f"https://{SHOP_NAME}.myshopify.com"

# Validate Helicone configuration
config_errors = HeliconeConfig.validate_config()
for error in config_errors:
    logger.error(f"Configuration error: {error}")

def call_gemini_via_helicone(prompt, user_id=None, session_id=None):
    """
    Enhanced Helicone integration with better observability
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Use the configuration helper functions
    headers = get_helicone_headers(
        request_id=request_id,
        user_id=user_id or "anonymous",
        session_id=session_id or "default",
        prompt_length=len(prompt)
    )
    
    data = get_request_data(prompt)
    
    try:
        logger.info(f"Making Helicone request - ID: {request_id}, User: {user_id}, Prompt length: {len(prompt)}")
        
        response = requests.post(
            HeliconeConfig.get_gateway_url(),
            headers=headers,
            json=data,
            timeout=HeliconeConfig.REQUEST_TIMEOUT
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Log response metrics
        logger.info(f"Helicone response - ID: {request_id}, Status: {response.status_code}, Time: {response_time:.2f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract response text
            try:
                response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Log success metrics
                logger.info(f"Helicone success - ID: {request_id}, Response length: {len(response_text)}")
                
                return response_text
                
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse Helicone response - ID: {request_id}, Error: {e}")
                return "Sorry, I couldn't parse the response from Gemini."
                
        else:
            logger.error(f"Helicone API error - ID: {request_id}, Status: {response.status_code}, Response: {response.text}")
            return f"Sorry, I encountered an error (Status: {response.status_code}). Please try again."
            
    except requests.exceptions.Timeout:
        logger.error(f"Helicone request timeout - ID: {request_id}")
        return "Sorry, the request timed out. Please try again."
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Helicone request failed - ID: {request_id}, Error: {e}")
        return "Sorry, I couldn't connect to the AI service. Please try again."
        
    except Exception as e:
        logger.error(f"Unexpected error in Helicone call - ID: {request_id}, Error: {e}")
        return "Sorry, an unexpected error occurred. Please try again."

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

def generate_chatbot_response(query, product_data, memory=None, user_id=None, session_id=None):
    query_lower = query.lower()
    
    # Log user query for observability
    logger.info(f"Processing query - User: {user_id}, Session: {session_id}, Query: {query[:100]}...")
    
    # Intercept direct product list queries before any LLM/Helicone logic
    product_list_phrases = [
        "product list", "list products", "show me products", "give me product list",
        "show products", "all products", "products list"
    ]
    if any(phrase in query_lower for phrase in product_list_phrases):
        product_info = []
        for i, product in enumerate(product_data[:10]):  # Show up to 10 products
            title = product.get('title', 'N/A')
            price = product.get('variants', [{}])[0].get('price', 'N/A')
            link = generate_product_link(product)
            if link:
                product_info.append(f'<a href="{link}">{title}</a> - ${price}')
            else:
                product_info.append(f'{title} - ${price}')
        return "Here are some of our products:<br>" + "<br>".join(product_info)
    
    # Always use Helicone for complex queries or when no user_id is provided (Shopify requests)
    should_use_helicone = (
        user_id is None or 
        user_id == 'anonymous' or 
        len(query.split()) > 3 or  # Complex queries
        any(word in query_lower for word in ['explain', 'what is', 'how does', 'why', 'tell me about', 'describe'])
    )
    
    if should_use_helicone:
        logger.info(f"Using Helicone for query: {query[:50]}... (user_id: {user_id})")
        return call_gemini_via_helicone(query, user_id or 'shopify-user', session_id or 'shopify-session')
    
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
            # Fallback: ask Gemini for a general answer with enhanced observability
            return call_gemini_via_helicone(query, user_id or 'shopify-user', session_id or 'shopify-session')

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    """Serve the web UI"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Starky Shop Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        .chat-container { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .chat-header { background: #007bff; color: white; padding: 15px; text-align: center; }
        .chat-messages { height: 400px; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 15px; max-width: 70%; }
        .user-message { background: #007bff; color: white; margin-left: auto; }
        .bot-message { background: #e9ecef; color: #333; }
        .input-container { display: flex; padding: 15px; border-top: 1px solid #dee2e6; }
        #messageInput { flex: 1; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; margin-right: 10px; }
        #sendButton { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .debug-info { background: #f8f9fa; padding: 10px; margin-top: 20px; border-radius: 5px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🛍️ Starky Shop Chatbot</h2>
            <p>Ask me about products, prices, or anything else!</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">Hello! Welcome to Starky Shop. How can I help you today?</div>
        </div>
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <div class="debug-info">
        <strong>Debug Info:</strong><br>
        User ID: <span id="userId">web-user-123</span><br>
        Session ID: <span id="sessionId">web-session-456</span><br>
        API Endpoint: <span id="apiEndpoint">http://localhost:5000/chat</span><br>
        <button onclick="testHelicone()" style="margin-top: 10px; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">Test Helicone Integration</button>
    </div>

    <script>
        let userId = 'web-user-' + Math.random().toString(36).substr(2, 9);
        let sessionId = 'web-session-' + Math.random().toString(36).substr(2, 9);
        
        document.getElementById('userId').textContent = userId;
        document.getElementById('sessionId').textContent = sessionId;
        
        function handleKeyPress(event) { if (event.key === 'Enter') sendMessage(); }
        
        function addMessage(message, isUser = false) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.innerHTML = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        async function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            messageInput.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        user_id: userId,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                if (data.error) {
                    addMessage('Error: ' + data.error);
                } else {
                    addMessage(data.response);
                }
            } catch (error) {
                addMessage('Error: Could not connect to the server.');
                console.error('Error:', error);
            }
        }
        
        function testHelicone() {
            document.getElementById('messageInput').value = "Explain quantum physics in simple terms";
            sendMessage();
        }
    </script>
</body>
</html>'''
    return html_content

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('message', '') if data else ''
    user_id = data.get('user_id', 'anonymous') if data else 'anonymous'
    session_id = data.get('session_id', 'default') if data else 'default'
    
    # Log incoming request
    logger.info(f"Chat request - User: {user_id}, Session: {session_id}, Query: {user_query[:50]}...")
    
    if not user_query:
        return jsonify({'error': 'No message provided'}), 400
    
    # Log incoming request
    logger.info(f"Chat request received - User: {user_id}, Session: {session_id}")
    
    answer = generate_chatbot_response(user_query, products, user_id=user_id, session_id=session_id)
    html_answer = markdown.markdown(answer)
    
    # Log response
    logger.info(f"Chat response sent - User: {user_id}, Response length: {len(answer)}")
    
    return jsonify({'response': html_answer})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'helicone_configured': HeliconeConfig.is_configured(),
        'google_api_configured': bool(HeliconeConfig.GOOGLE_API_KEY),
        'products_loaded': len(products) if products else 0
    })

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
