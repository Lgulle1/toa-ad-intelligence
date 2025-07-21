import logging
import traceback

# Set up comprehensive logging to catch ALL warnings
class DebugLoggingHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()
        print(f"DEBUG: All logging - {record.levelname}: {message} (from {record.name})")
        if any(phrase in message.lower() for phrase in ["chrome browser check failed", "chrome", "browser check", "install chrome"]):
            print(f"\n\n=== FOUND CHROME WARNING ===")
            print(f"Message: {message}")
            print(f"Logger: {record.name}")
            print(f"Level: {record.levelname}")
            print(f"Module: {record.module}")
            print(f"Function: {record.funcName}")
            print(f"Line: {record.lineno}")
            print("Stack trace:")
            traceback.print_stack()
            print("=== END CHROME WARNING ===\n\n")

# Add handler to root logger and all possible loggers
debug_handler = DebugLoggingHandler()
debug_handler.setLevel(logging.DEBUG)

logging.getLogger().addHandler(debug_handler)
logging.getLogger("__main__").addHandler(debug_handler)
logging.getLogger("app").addHandler(debug_handler)

# Also override the warning function directly
original_warning = logging.warning
def patched_warning(msg, *args, **kwargs):
    print(f"\n\n!!! DIRECT WARNING CALL: {msg} !!!")
    traceback.print_stack()
    print("!!! END DIRECT WARNING !!!\n\n")
    return original_warning(msg, *args, **kwargs)

logging.warning = patched_warning

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