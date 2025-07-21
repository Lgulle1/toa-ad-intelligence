from flask import Flask, render_template, request, jsonify, flash
import logging
import os
from dotenv import load_dotenv
import sys
import warnings

# AGGRESSIVE Chrome warning suppression
class ChromeWarningFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        blocked_phrases = [
            "chrome browser check failed",
            "install chrome",
            "chrome not found",
            "browser check failed",
            "install chrome or chromium",
            "chrome or chromium for full functionality"
        ]
        
        for phrase in blocked_phrases:
            if phrase in msg:
                return False  # Block this message completely
        return True

# Apply the filter to all loggers, especially __main__
root_logger = logging.getLogger()
main_logger = logging.getLogger('__main__')
app_logger = logging.getLogger('app')
werkzeug_logger = logging.getLogger('werkzeug')

# Apply filter to all possible loggers
for logger in [root_logger, main_logger, app_logger, werkzeug_logger]:
    logger.addFilter(ChromeWarningFilter())

# Set main logger level to ERROR to suppress warnings
main_logger.setLevel(logging.ERROR)

# Additional nuclear option - disable all __main__ warnings during startup
original_showwarning = warnings.showwarning
def silence_chrome_warnings(message, category, filename, lineno, file=None, line=None):
    msg_str = str(message).lower()
    if any(phrase in msg_str for phrase in ["chrome", "browser check", "install chrome"]):
        return  # Completely ignore Chrome-related warnings
    return original_showwarning(message, category, filename, lineno, file, line)

warnings.showwarning = silence_chrome_warnings

# Also suppress warnings module
warnings.filterwarnings("ignore", message=".*Chrome.*")
warnings.filterwarnings("ignore", message=".*browser.*")

# Import scraper only when needed to avoid early Chrome checks
# from scraper import MetaAdScraper

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
        # Import scraper only when needed
        from scraper import MetaAdScraper
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
        # Import scraper only when needed
        from scraper import MetaAdScraper
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