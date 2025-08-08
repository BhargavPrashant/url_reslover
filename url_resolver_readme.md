# URL Resolver Service 🔗

A lightweight Flask-based web service that resolves URLs, with specialized support for Google News article links. This service can decode shortened Google News URLs and resolve standard URL redirects.

## Features ✨

- **Google News URL Decoding**: Automatically decode Google News article URLs to their original sources
- **Standard URL Resolution**: Follow redirects and resolve final URLs for any web link
- **RESTful API**: Simple HTTP endpoints for single and batch URL resolution
- **Health Monitoring**: Built-in health check endpoint for monitoring
- **Error Handling**: Comprehensive error handling with detailed logging
- **Rate Limiting**: Built-in protection with batch processing limits

## Installation 📦

### Prerequisites
- Python 3.7+
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Python Packages
```
requests
beautifulsoup4
flask
```

Or install manually:
```bash
pip install requests beautifulsoup4 flask
```

## Usage 🚀

### Starting the Server

#### Basic Usage
```bash
python working_resolver.py
```

#### Custom Configuration
```bash
python working_resolver.py --port 8000 --host 0.0.0.0 --debug
```

#### Command Line Options
- `--port`: Server port (default: 5000)
- `--host`: Host address (default: 0.0.0.0)
- `--debug`: Enable debug mode

### API Endpoints 📡

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "URL Resolver",
  "timestamp": 1691499696.123
}
```

#### 2. Resolve Single URL
```http
GET /resolve?url=<encoded_url>
```

**Example:**
```bash
curl 'http://localhost:5000/resolve?url=https://news.google.com/articles/CBMiX2h0dHBzOi8vd3d3LmV4YW1wbGUuY29tL2FydGljbGUv'
```

**Response:**
```json
{
  "original": "https://news.google.com/articles/CBMiX...",
  "final_url": "https://www.example.com/article/",
  "status_code": 200,
  "method": "google_news"
}
```

#### 3. Batch URL Resolution
```http
POST /resolve-batch
Content-Type: application/json

{
  "urls": [
    "https://news.google.com/articles/...",
    "https://bit.ly/example",
    "https://t.co/example"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "original": "https://news.google.com/articles/...",
      "final_url": "https://www.example.com/article/",
      "status_code": 200,
      "method": "google_news"
    },
    {
      "original": "https://bit.ly/example",
      "final_url": "https://www.example.com/",
      "status_code": 200,
      "method": "standard"
    }
  ]
}
```

## Public Access with ngrok 🌐

To make your local server publicly accessible:

### 1. Install ngrok
```bash
# Download from https://ngrok.com/download
# Or via package managers:
npm install -g ngrok
# choco install ngrok (Windows)
```

### 2. Set up authentication
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 3. Start your Flask app
```bash
python working_resolver.py --port 8000
```

### 4. Create public tunnel
```bash
ngrok http 8000
```

Your service will be available at the provided ngrok URL (e.g., `https://abc123.ngrok-free.app`)

## Docker Support 🐳

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY working_resolver.py .

EXPOSE 5000
CMD ["python", "working_resolver.py", "--host", "0.0.0.0"]
```

### Build and Run
```bash
docker build -t url-resolver .
docker run -p 5000:5000 url-resolver
```

## Error Handling 🛠️

The service handles various error scenarios:

- **Invalid URLs**: Returns error message with status code
- **Network timeouts**: 10-second timeout for standard requests, 15 seconds for Google News
- **Rate limiting**: Batch requests limited to 10 URLs
- **Server errors**: Comprehensive error logging and user-friendly responses

## How It Works ⚙️

### Google News URL Decoding
1. Extracts article ID from Google News URL
2. Fetches decoding parameters from Google News page
3. Uses Google's batchexecute endpoint to decode the URL
4. Returns the original article URL

### Standard URL Resolution
1. Follows HTTP redirects using requests library
2. Returns the final destination URL
3. Includes status codes and error information

## Development 💻

### Project Structure
```
url-resolver/
├── working_resolver.py    # Main application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── Dockerfile            # Docker configuration
```

### Adding Features
The `URLResolver` class can be easily extended with additional URL decoding methods for other news aggregators or URL shorteners.

### Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test URL resolution
curl 'http://localhost:5000/resolve?url=https://example.com'

# Test batch resolution
curl -X POST http://localhost:5000/resolve-batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://google.com"]}'
```

## Security Considerations 🔒

- **Rate Limiting**: Batch requests limited to 10 URLs
- **Timeout Protection**: All HTTP requests have timeout limits
- **Input Validation**: URL parameters are validated
- **Error Sanitization**: Sensitive error details are not exposed

## Deployment 🚀

### Production Considerations
- Use a production WSGI server (gunicorn, uWSGI)
- Set up reverse proxy (nginx)
- Configure proper logging
- Set up monitoring and health checks
- Use environment variables for configuration

### Example with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 working_resolver:app
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License 📄

This project is open source and available under the [MIT License](LICENSE).

## Support 💬

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for URL resolution needs**