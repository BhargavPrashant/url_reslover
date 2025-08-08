#!/usr/bin/env python3

import argparse
import json
import logging
import requests
import sys
import time
from urllib.parse import urlparse, quote
import base64
import re
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class URLResolver:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_decoding_params(self, gn_art_id):
        try:
            response = requests.get(f"https://news.google.com/rss/articles/{gn_art_id}", 
                                  headers=self.headers, timeout=10)
            if response.status_code != 200:
                response = requests.get(f"https://news.google.com/articles/{gn_art_id}", 
                                      headers=self.headers, timeout=10)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            div = soup.select_one("c-wiz > div")
            
            if not div:
                return None
                
            return {
                "signature": div.get("data-n-a-sg"),
                "timestamp": div.get("data-n-a-ts"),
                "gn_art_id": gn_art_id,
            }
        except Exception as e:
            logging.error(f"Error getting decoding params: {str(e)}")
            return None

    def decode_google_news_url_batchexecute(self, url):
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split("/")
            
            if "articles" not in path_parts:
                return None
                
            gn_art_id = path_parts[-1]
            params = self.get_decoding_params(gn_art_id)
            if not params:
                return None
            
            articles_req = [
                "Fbv4je",
                f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{params["gn_art_id"]}",{params["timestamp"]},"{params["signature"]}"]'
            ]
            
            payload = f"f.req={quote(json.dumps([[articles_req]]))}"
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "User-Agent": self.headers["User-Agent"],
                "Referer": "https://news.google.com/",
            }
            
            response = requests.post(
                "https://news.google.com/_/DotsSplashUi/data/batchexecute",
                headers=headers,
                data=payload,
                timeout=15
            )
            
            response.raise_for_status()
            response_parts = response.text.split("\n\n")
            
            if len(response_parts) >= 2:
                try:
                    decoded_response = json.loads(response_parts[1])
                    if len(decoded_response) > 0 and len(decoded_response[0]) > 2:
                        decoded_url = json.loads(decoded_response[0][2])[1]
                        return decoded_url
                except:
                    pass
            
            return None
        except Exception as e:
            logging.error(f"Error in batchexecute: {str(e)}")
            return None

    def resolve_single_url(self, url):
        try:
            if "news.google.com" in url:
                resolved_url = self.decode_google_news_url_batchexecute(url)
                if resolved_url and resolved_url.startswith('http'):
                    return {
                        "original": url,
                        "final_url": resolved_url,
                        "status_code": 200,
                        "method": "google_news"
                    }

            # Standard URL resolution
            response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=10)
            
            return {
                "original": url,
                "final_url": response.url,
                "status_code": response.status_code,
                "method": "standard"
            }

        except Exception as e:
            return {
                "original": url,
                "error": str(e),
                "status_code": 500
            }

# Create Flask app
app = Flask(__name__)
resolver = URLResolver()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "URL Resolver",
        "status": "running",
        "version": "1.0",
        "endpoints": ["/health", "/resolve", "/resolve-batch"]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "URL Resolver",
        "timestamp": time.time()
    })

@app.route('/resolve', methods=['GET'])
def resolve():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400
    
    result = resolver.resolve_single_url(url)
    return jsonify(result)

@app.route('/resolve-batch', methods=['POST'])
def resolve_batch():
    try:
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({"error": "Missing urls in JSON"}), 400
        
        urls = data['urls'][:10]  # Limit to 10
        results = []
        
        for url in urls:
            result = resolver.resolve_single_url(url)
            results.append(result)
        
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    print(f"🚀 URL Resolver Server")
    print(f"📍 Starting on {args.host}:{args.port}")
    print(f"📝 Endpoints available:")
    print(f"   GET  /health")
    print(f"   GET  /resolve?url=<url>")
    print(f"   POST /resolve-batch")
    print(f"\n💡 Test with:")
    print(f"   curl http://localhost:{args.port}/health")
    print(f"   curl 'http://localhost:{args.port}/resolve?url=https://example.com'")
    print(f"\nStarting server...")
    print("-" * 50)
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
