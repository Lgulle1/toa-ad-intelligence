# Meta Ad Library Scraper

A full-stack web application built with Python Flask that scrapes and analyzes active ads from Meta's public Ad Library. Users can search for ads by keyword and view detailed information including advertiser names, headlines, ad text, media URLs, and start dates.

## ✨ Features

- 🔍 **Real-time Search**: Search Meta's Ad Library for active ads by keyword
- 📊 **Detailed Results**: Extract advertiser name, headline, ad text, media URL, and start date
- 🎨 **Modern UI**: Beautiful, responsive web interface with Bootstrap styling
- 🚀 **REST API**: Programmatic access via JSON API endpoints
- 🔧 **Extensible**: Modular design for easy extension to other ad platforms
- 🤖 **Browser Automation**: Uses Selenium with Chrome/Chromium for JavaScript handling
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# 1. Clone or download the project
git clone <repository-url>
cd meta-ad-scraper

# 2. Run the automated setup
python3 setup.py

# 3. Start the application
./run.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Chrome/Chromium browser
sudo apt install chromium-browser  # Ubuntu/Debian
# or
brew install --cask google-chrome  # macOS

# 4. Run the application
python app.py
```

**🌐 Access the app**: Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
meta-ad-scraper/
├── app.py              # Flask application entry point
├── scraper.py          # Web scraping logic with Selenium
├── requirements.txt    # Python dependencies
├── setup.py           # Automated setup script
├── run.sh             # Quick start script
├── .env               # Environment configuration
├── README.md          # This file
└── templates/         # HTML templates
    ├── base.html      # Base template with styling
    ├── index.html     # Search page
    ├── results.html   # Results display page
    ├── 404.html       # 404 error page
    └── 500.html       # 500 error page
```

## 💻 Usage

### Web Interface

1. **Search Page**: Enter a keyword (e.g., "orthopedic", "knee surgery") in the search box
2. **Results**: View up to 10 relevant ads with detailed information
3. **Navigation**: Use the back button to return to search

### API Access

The application provides a REST API for programmatic access:

```bash
# Search for ads via API
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "orthopedic"}'
```

**Response format:**
```json
{
  "keyword": "orthopedic",
  "count": 5,
  "ads": [
    {
      "advertiser_name": "Orthopedic Solutions Inc.",
      "headline": "Best Orthopedic Services Available Now",
      "text": "Discover top-quality orthopedic solutions...",
      "media_url": "https://via.placeholder.com/400x300?text=Ad+Image+1",
      "start_date": "2024-01-15"
    }
  ]
}
```

## ⚙️ Configuration

### Environment Variables

Create or modify `.env` file:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Scraper Configuration
SCRAPER_TIMEOUT=30
MAX_RESULTS=10

# Browser Configuration
BROWSER_HEADLESS=True
```

### Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
2. Use a strong `SECRET_KEY`
3. Consider using a WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 🔧 Technical Details

### Scraping Strategy

- **Primary Tool**: Selenium with Chrome/Chromium for JavaScript-heavy sites
- **Browser Options**: Headless mode, optimized performance settings
- **Resilience**: Mock data generation when scraping fails (for demonstration)
- **Rate Limiting**: Built-in delays to respect Meta's servers

### Browser Support

- **Chrome**: Full support
- **Chromium**: Full support (recommended for Linux)
- **Other browsers**: Not supported (Selenium configured for Chrome)

### Error Handling

- Graceful fallback to mock data if scraping fails
- Comprehensive logging for debugging
- User-friendly error messages
- Proper HTTP status codes for API responses

## 🚀 Extending the Application

### Adding Google Ads Support

1. **Create a new scraper class** in `scraper.py`:
   ```python
   class GoogleAdsScraper:
       def search_ads(self, keyword):
           # Implementation for Google Ads
           pass
   ```

2. **Add a new route** in `app.py`:
   ```python
   @app.route('/search/google', methods=['POST'])
   def search_google():
       # Use GoogleAdsScraper
       pass
   ```

3. **Update templates** to include Google Ads option

### Adding Database Storage

1. **Add SQLAlchemy** to requirements.txt
2. **Create models** for storing ad data
3. **Add database routes** for historical data
4. **Create analytics** views for trend analysis

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/Chromium not found**
   ```bash
   # Ubuntu/Debian
   sudo apt install chromium-browser
   
   # CentOS/RHEL
   sudo yum install chromium
   
   # macOS
   brew install --cask google-chrome
   ```

2. **Virtual environment issues**
   ```bash
   # Remove and recreate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission errors on Linux**
   ```bash
   chmod +x run.sh
   chmod +x setup.py
   ```

4. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`
   - Or kill the existing process: `lsof -ti:5000 | xargs kill`

### Debug Mode

For detailed debugging, check the console output when running:

```bash
source venv/bin/activate
python app.py
```

Look for:
- Browser initialization messages
- Scraping progress logs
- Error messages with stack traces

## 📋 Dependencies

- **Flask 3.0.0**: Web framework
- **Selenium 4.15.0**: Browser automation
- **Requests 2.31.0**: HTTP requests (fallback)
- **BeautifulSoup4 4.12.2**: HTML parsing (fallback)
- **python-dotenv 1.0.0**: Environment variable management

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚖️ Legal and Ethical Considerations

- This tool only accesses **publicly available** data from Meta's Ad Library
- Respects rate limits and server resources
- Use responsibly and in compliance with Meta's terms of service
- For research and analysis purposes only
- No personal data is collected or stored

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Check the console logs for error messages
4. Ensure you have a stable internet connection
5. Make sure Chrome/Chromium is properly installed

## 📄 Example Keywords

Try searching for these terms to test the application:

- `orthopedic` - Medical devices and services
- `knee surgery` - Surgical procedures
- `fitness` - Health and wellness
- `weight loss` - Diet and exercise
- `real estate` - Property listings
- `education` - Online courses
- `technology` - Software and hardware

---

**🎉 Happy scraping!** 

Made with ❤️ using Flask, Selenium, and Bootstrap.
