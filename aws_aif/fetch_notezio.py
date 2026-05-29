#!/usr/bin/env python3
"""
Fetch questions from notezio.com practice tests
"""

import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

OUTPUT_DIR = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped")

def fetch_notezio_test(test_url):
    """Fetch questions from a notezio practice test"""
    url = f"https://notezio.com{test_url}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            questions = []
            
            # Look for question elements
            # Try different patterns
            q_elements = soup.find_all(['div', 'p', 'h3'], string=re.compile(r'Question\s*\d+'))
            
            if not q_elements:
                # Try finding by class or structure
                q_elements = soup.find_all('div', class_=re.compile(r'question'))
            
            print(f"  Found {len(q_elements)} question elements")
            
            # For now, just return the HTML structure info
            return {
                'url': url,
                'status': response.status_code,
                'content_length': len(response.text),
                'question_elements': len(q_elements)
            }
        
    except Exception as e:
        print(f"  Error: {e}")
    
    return None

def main():
    print("Fetching practice tests from notezio.com...")
    
    test_urls = [
        '/aws-certified-ai-practitioner/practice-test/practice-test-1/',
        '/aws-certified-ai-practitioner/practice-test/practice-test-2/',
        '/aws-certified-ai-practitioner/practice-test/practice-test-3/',
        '/aws-certified-ai-practitioner/practice-test/practice-test-4/'
    ]
    
    results = []
    for url in test_urls:
        print(f"\nFetching {url}...")
        result = fetch_notezio_test(url)
        if result:
            results.append(result)
            print(f"  Status: {result['status']}, Length: {result['content_length']}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary:")
    for r in results:
        print(f"  {r['url']}: {r['question_elements']} questions")

if __name__ == '__main__':
    main()
