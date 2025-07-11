# Starky Shop Chatbot with Helicone LLM Observability

A smart e-commerce chatbot with comprehensive LLM observability using Helicone for monitoring, tracking, and analyzing all AI interactions.

## 🚀 Features

- **Smart Product Search**: Find products by name, category, or description
- **LLM Integration**: Powered by Google Gemini via Helicone proxy
- **Real-time Observability**: Track all LLM requests with detailed metrics
- **User Session Management**: Monitor user interactions and behavior
- **Performance Monitoring**: Response times, token usage, and success rates
- **Web UI**: Clean, responsive chat interface
- **API Endpoint**: RESTful API for integration with any frontend

## 📁 Project Structure

```
temp_chatbot_v2/
├── data/
│   ├── app.py              # Main Flask application
│   ├── products.json       # Product database
│   └── scraper.py          # Product scraper (optional)
├── helicone_config.py      # Helicone configuration
├── test_helicone.py        # Helicone integration tests
├── setup_helicone.py       # Setup and validation script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── config.py              # Basic configuration
└── README.md              # This file
```

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file with your API keys:
```env
HELICONE_API_KEY=your_helicone_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
SHOPIFY_API_KEY=your_shopify_api_key_here
SHOP_NAME=your_shop_name_here
```

### 3. Validate Setup
```bash
python3 setup_helicone.py
```

### 4. Run Tests
```bash
python3 test_helicone.py
```

## 🚀 Usage

### Start the Application
```bash
python3 data/app.py api
```

### Access the Web UI
- **Local**: http://localhost:5000
- **API Endpoint**: http://localhost:5000/chat

### API Usage
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me some perfumes",
    "user_id": "user-123",
    "session_id": "session-456"
  }'
```

## 📊 Monitoring

### Helicone Dashboard
Visit [https://www.helicone.ai/](https://www.helicone.ai/) to monitor:
- Request logs and timestamps
- Performance metrics and response times
- User analytics and session tracking
- Cost analysis and token usage
- Error rates and debugging

### Health Check
```bash
curl http://localhost:5000/health
```

## 🔧 Configuration

### Helicone Settings
Edit `helicone_config.py` to customize:
- Model parameters (temperature, max tokens)
- Caching settings
- Request timeouts
- Custom properties

### Product Database
Update `data/products.json` with your product catalog.

## 🧪 Testing

### Run Integration Tests
```bash
python3 test_helicone.py
```

### Test Different Scenarios
- Product queries
- Complex questions (triggers Helicone)
- Error handling
- Performance metrics

## 📈 Observability Features

- **Request Tracking**: Unique IDs for every request
- **User Analytics**: Track by user and session
- **Performance Metrics**: Response times and token usage
- **Error Monitoring**: Comprehensive error handling
- **Custom Properties**: Rich metadata for each request
- **Caching Support**: Cost optimization

## 🔍 Troubleshooting

### Common Issues
1. **401 Errors**: Check API keys in `.env`
2. **Import Errors**: Ensure all dependencies are installed
3. **No Helicone Logs**: Verify Helicone API key is valid
4. **Slow Responses**: Check network connectivity

### Debug Mode
Enable detailed logging by setting log level to DEBUG in `app.py`.

## 📚 API Reference

### POST /chat
Send a message to the chatbot.

**Request:**
```json
{
  "message": "string",
  "user_id": "string (optional)",
  "session_id": "string (optional)"
}
```

**Response:**
```json
{
  "response": "string (HTML formatted)"
}
```

### GET /health
Check application health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "helicone_configured": true,
  "google_api_configured": true,
  "products_loaded": 17
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Helicone Documentation**: [https://docs.helicone.ai/](https://docs.helicone.ai/)
- **Google AI Studio**: [https://makersuite.google.com/](https://makersuite.google.com/)
- **Issues**: Create an issue in this repository 