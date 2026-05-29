#!/usr/bin/env python3
"""
Fetch more questions from additional sources
"""

import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

OUTPUT_DIR = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped")

def fetch_masteryexamprep():
    """Fetch questions from masteryexamprep.com"""
    url = "https://masteryexamprep.com/exams/aws/aif-c01/free-practice-exam/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            questions = []
            
            # Look for question patterns
            # The site uses markdown-style questions
            text = response.text
            
            # Find question blocks
            q_pattern = r'### Question (\d+).*?(?=### Question|\Z)'
            q_blocks = re.findall(q_pattern, text, re.DOTALL)
            
            print(f"Found {len(q_blocks)} question blocks")
            return []
        
    except Exception as e:
        print(f"Error fetching masteryexamprep: {e}")
    
    return []

def fetch_notezio():
    """Fetch questions from notezio.com"""
    url = "https://notezio.com/aws-certified-ai-practitioner/practice-test/tests/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find links to practice tests
            links = soup.find_all('a', href=re.compile(r'practice-test'))
            print(f"Found {len(links)} practice test links")
            
            for link in links[:5]:  # Check first 5
                print(f"  {link.get('href')}")
            
            return []
        
    except Exception as e:
        print(f"Error fetching notezio: {e}")
    
    return []

def main():
    print("Fetching from additional sources...")
    
    # Try masteryexamprep
    print("\n1. masteryexamprep.com:")
    fetch_masteryexamprep()
    
    # Try notezio
    print("\n2. notezio.com:")
    fetch_notezio()
    
    # Check what we have so far
    additional_file = OUTPUT_DIR / "additional_questions.txt"
    if additional_file.exists():
        with open(additional_file, 'r') as f:
            content = f.read()
            q_count = content.count('Q#:')
            print(f"\nCurrent additional questions: {q_count}")

if __name__ == '__main__':
    main()
