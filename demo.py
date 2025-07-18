#!/usr/bin/env python3
"""
Demo script for Meta Ad Library Scraper
This script demonstrates how to use the scraper programmatically
"""

import requests
import json
import time
from scraper import MetaAdScraper

def demo_api():
    """Demo using the REST API"""
    print("🔍 Demo: Using REST API")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    keywords = ["orthopedic", "fitness", "real estate"]
    
    for keyword in keywords:
        print(f"\n🔎 Searching for: {keyword}")
        
        try:
            response = requests.post(
                f"{base_url}/api/search",
                json={"keyword": keyword},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['count']} ads")
                
                # Show first ad
                if data['ads']:
                    first_ad = data['ads'][0]
                    print(f"   📢 Advertiser: {first_ad['advertiser_name']}")
                    print(f"   📝 Headline: {first_ad['headline']}")
                    print(f"   📅 Start Date: {first_ad['start_date']}")
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
        
        time.sleep(1)  # Be nice to the server

def demo_direct():
    """Demo using the scraper directly"""
    print("\n🔍 Demo: Using Scraper Directly")
    print("=" * 40)
    
    scraper = MetaAdScraper()
    keyword = "technology"
    
    print(f"\n🔎 Searching for: {keyword}")
    
    try:
        ads = scraper.search_ads(keyword)
        print(f"✅ Found {len(ads)} ads")
        
        # Show all ads
        for i, ad in enumerate(ads, 1):
            print(f"\n📢 Ad {i}:")
            print(f"   Company: {ad['advertiser_name']}")
            print(f"   Headline: {ad['headline']}")
            print(f"   Text: {ad['text'][:60]}...")
            print(f"   Start Date: {ad['start_date']}")
            
    except Exception as e:
        print(f"❌ Scraper Error: {e}")

def main():
    """Main demo function"""
    print("🚀 Meta Ad Library Scraper Demo")
    print("=" * 50)
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
            demo_api()
        else:
            print("⚠️  Flask app not responding properly")
    except requests.exceptions.RequestException:
        print("❌ Flask app not running. Start it with: python app.py")
        print("   Continuing with direct scraper demo...")
    
    demo_direct()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n📍 Web Interface: http://localhost:5000")
    print("📖 API Documentation: See README.md")

if __name__ == "__main__":
    main()