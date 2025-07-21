# ULTIMATE DEBUG - Hook into EVERYTHING
import sys
import warnings
import logging
import traceback
import os

print("🚀 ULTIMATE DEBUG: Starting complete system hook...")

# Hook into warnings module
original_warn = warnings.warn
def debug_warn(message, category=UserWarning, filename='', lineno=-1, file=None, stacklevel=1):
    print(f"\n⚠️  WARNINGS MODULE: {message}")
    traceback.print_stack()
    print("⚠️  END WARNINGS\n")
    return original_warn(message, category, filename, lineno, file, stacklevel)

warnings.warn = debug_warn

# Hook into sys.stderr
original_stderr_write = sys.stderr.write
def debug_stderr(text):
    if "chrome" in text.lower() or "browser" in text.lower():
        print(f"\n💥 STDERR WRITE: {text}")
        traceback.print_stack()
        print("💥 END STDERR\n")
    return original_stderr_write(text)

sys.stderr.write = debug_stderr

# Hook into print function
original_print = print
def debug_print(*args, **kwargs):
    text = ' '.join(str(arg) for arg in args)
    if "chrome" in text.lower() and "browser" in text.lower():
        print("📢 PRINT HOOK:", text)
        traceback.print_stack()
        print("📢 END PRINT HOOK\n")
    return original_print(*args, **kwargs)

# Don't override print yet as we need it for our debug output

# Hook ALL logging
class UltimateLoggingInterceptor:
    def __init__(self):
        self.original_handle = logging.Logger.handle
        self.original_warning = logging.warning
        self.original_basicConfig = logging.basicConfig
        
    def hook_everything(self):
        def debug_handle(self, record):
            msg = record.getMessage()
            if "chrome" in msg.lower() or "browser" in msg.lower():
                print(f"\n🎯 LOGGER.HANDLE: {msg}")
                print(f"Logger: {record.name}")
                print(f"Level: {record.levelname}")
                traceback.print_stack()
                print("🎯 END LOGGER.HANDLE\n")
            return self.original_handle(record)
            
        def debug_warning(msg, *args, **kwargs):
            if "chrome" in str(msg).lower() or "browser" in str(msg).lower():
                print(f"\n⚡ LOGGING.WARNING: {msg}")
                traceback.print_stack()
                print("⚡ END LOGGING.WARNING\n")
            return self.original_warning(msg, *args, **kwargs)
        
        logging.Logger.handle = debug_handle
        logging.warning = debug_warning

interceptor = UltimateLoggingInterceptor()
interceptor.hook_everything()

print("🚀 ULTIMATE DEBUG: All hooks installed, importing modules...")
print("🔍 If the Chrome warning appears without our debug output, it's from subprocess/external source")

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