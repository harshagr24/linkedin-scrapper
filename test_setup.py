#!/usr/bin/env python3
"""
Simple test script to verify scraper setup
"""

import sys
from pathlib import Path

def main():
    """Quick setup verification."""
    print("🔍 LinkedIn Scraper - Setup Check")
    print("=" * 35)
    
    checks_passed = 0
    total_checks = 4
    
    # Check 1: Dependencies
    try:
        import selenium, bs4, pandas
        print("✅ Dependencies installed")
        checks_passed += 1
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
    
    # Check 2: Configuration
    try:
        import json
        with open('config.json', 'r') as f:
            config = json.load(f)
        if 'scraping' in config and 'browser' in config:
            print("✅ Configuration valid")
            checks_passed += 1
        else:
            print("❌ Invalid configuration")
    except Exception:
        print("❌ Configuration file missing/invalid")
    
    # Check 3: Profile URLs
    urls_file = Path('data/profile_urls.txt')
    if urls_file.exists():
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if urls:
            print(f"✅ Found {len(urls)} profile URLs")
            checks_passed += 1
        else:
            print("❌ No profile URLs found")
    else:
        print("❌ Profile URLs file missing")
    
    # Check 4: Output directory
    output_dir = Path('data/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Output directory ready")
    checks_passed += 1
    
    # Results
    print(f"\n📊 Setup Status: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All good! Run: python main.py")
    else:
        print("⚠️  Please fix the issues above")

if __name__ == "__main__":
    main()