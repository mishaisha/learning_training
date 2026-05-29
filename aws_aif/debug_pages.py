#!/usr/bin/env python3
"""
Check page structure and debug why pages 23-43 return 0 questions
"""

import requests
import re
from bs4 import BeautifulSoup

def check_page(page_num):
    """Check a single page"""
    url = f"https://free-braindumps.com/amazon/free-aif-c01-braindumps/page-{page_num}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        panels = soup.find_all('div', class_='panel panel-default')
        
        # Check for question numbers
        question_numbers = []
        for panel in panels:
            heading = panel.find('strong', class_='text-uppercase')
            if heading:
                text = heading.get_text(strip=True)
                match = re.search(r'QUESTION:\s*(\d+)', text)
                if match:
                    question_numbers.append(int(match.group(1)))
        
        return {
            'status': response.status_code,
            'panels': len(panels),
            'question_numbers': question_numbers,
            'content_length': len(response.text)
        }
        
    except Exception as e:
        return {'error': str(e)}

# Test pages
test_pages = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
for page in test_pages:
    result = check_page(page)
    print(f"Page {page}: {result}")
