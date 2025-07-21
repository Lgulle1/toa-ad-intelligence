# IMMEDIATE DEBUG SETUP - MUST BE FIRST!
import logging
import traceback
import sys

print("🔍 DEBUG: Starting app.py import...")

# Set up the most aggressive debugging possible
class UltraDebugHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()
        print(f"🐛 ULTRA DEBUG: {record.levelname} from {record.name}: {message}")
        if "chrome" in message.lower() or "browser" in message.lower():
            print(f"\n🎯 === CHROME/BROWSER WARNING DETECTED ===")
            print(f"Full message: {message}")
            print(f"Logger name: {record.name}")
            print(f"Level: {record.levelname}")
            print(f"Module: {getattr(record, 'module', 'Unknown')}")
            print(f"Function: {getattr(record, 'funcName', 'Unknown')}")
            print(f"Line: {getattr(record, 'lineno', 'Unknown')}")
            print(f"Pathname: {getattr(record, 'pathname', 'Unknown')}")
            print("Complete stack trace:")
            traceback.print_stack()
            print("🎯 === END CHROME/BROWSER WARNING ===\n")

# Create and configure the ultra debug handler
ultra_handler = UltraDebugHandler()
ultra_handler.setLevel(logging.DEBUG)

# Add to ALL possible loggers
root_logger = logging.getLogger()
root_logger.addHandler(ultra_handler)
root_logger.setLevel(logging.DEBUG)

main_logger = logging.getLogger("__main__")
main_logger.addHandler(ultra_handler)
main_logger.setLevel(logging.DEBUG)

# Patch ALL warning functions
original_basicConfig = logging.basicConfig
original_warning = logging.warning
original_getLogger = logging.getLogger

def debug_warning(msg, *args, **kwargs):
    print(f"\n⚡ INTERCEPTED logging.warning(): {msg}")
    traceback.print_stack()
    print("⚡ END INTERCEPTED WARNING\n")
    return original_warning(msg, *args, **kwargs)

def debug_getLogger(name=None):
    logger = original_getLogger(name)
    logger.addHandler(ultra_handler)
    return logger

logging.warning = debug_warning
logging.getLogger = debug_getLogger

print("🔍 DEBUG: Logging setup complete, importing other modules...")

from flask import Flask, render_template, request, jsonify, flash
from scraper import MetaAdScraper
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main search page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests and return results"""
    keyword = request.form.get('keyword', '').strip()
    
    if not keyword:
        flash('Please enter a search keyword', 'error')
        return render_template('index.html')
    
    try:
        logger.info(f"Searching for keyword: {keyword}")
        scraper = MetaAdScraper()
        ads = scraper.search_ads(keyword)
        
        # Limit to top 10 results
        ads = ads[:10]
        
        logger.info(f"Found {len(ads)} ads for keyword: {keyword}")
        return render_template('results.html', ads=ads, keyword=keyword)
        
    except Exception as e:
        logger.error(f"Error searching for ads: {str(e)}")
        flash(f'Error occurred while searching: {str(e)}', 'error')
        return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for programmatic access"""
    data = request.get_json()
    keyword = data.get('keyword', '').strip() if data else None
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    try:
        scraper = MetaAdScraper()
        ads = scraper.search_ads(keyword)
        ads = ads[:10]  # Limit to top 10
        
        return jsonify({
            'keyword': keyword,
            'count': len(ads),
            'ads': ads
        })
        
    except Exception as e:
        logger.error(f"API Error searching for ads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)