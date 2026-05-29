#!/usr/bin/env python3
"""
Fetch and parse AWS AIF-C01 questions from free-braindumps.com (pages 9-43)
"""

import requests
import re
import json
import time
import html
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
BASE_URL = "https://free-braindumps.com/amazon/free-aif-c01-braindumps/page-{}"
START_PAGE = 9
END_PAGE = 43
OUTPUT_DIR = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped")
EXISTING_QUESTIONS_FILE = OUTPUT_DIR / "free-braindumps-questions.txt"

def clean_html(text):
    """Remove HTML tags and decode entities"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_questions_from_html(html_content, page_num):
    """Extract questions from HTML page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    questions = []
    
    # Find all question panels
    panels = soup.find_all('div', class_='panel panel-default')
    
    for panel in panels:
        try:
            # Extract question number
            heading = panel.find('strong', class_='text-uppercase')
            if not heading:
                continue
            
            q_text = heading.get_text(strip=True)
            q_match = re.search(r'QUESTION:\s*(\d+)', q_text)
            if not q_match:
                continue
            
            q_num = int(q_match.group(1))
            
            # Extract question text
            lead_p = panel.find('p', class_='lead')
            if not lead_p:
                continue
            
            # Get question text (before the options)
            question_parts = []
            for child in lead_p.children:
                if child.name == 'ol':
                    break
                question_parts.append(child.get_text() if hasattr(child, 'get_text') else str(child))
            
            question_text = clean_html(' '.join(question_parts))
            
            # Extract options
            ol = lead_p.find('ol')
            if not ol:
                continue
            
            options = []
            correct_answers = []
            
            for i, li in enumerate(ol.find_all('li')):
                option_text = clean_html(li.get_text())
                options.append(option_text)
                
                if li.get('data-correct') == 'True':
                    correct_answers.append(i)
            
            # Extract explanation
            explanation = ""
            answer_div = panel.find('div', id=f'answerQ{q_num}')
            if answer_div:
                bg_yellow = answer_div.find('div', class_='bg-light-yellow')
                if bg_yellow:
                    explanation = clean_html(bg_yellow.get_text())
            
            # Format question
            question = {
                'id': q_num,
                'page': page_num,
                'question': question_text,
                'options': options,
                'correct_answers': correct_answers,
                'explanation': explanation
            }
            
            questions.append(question)
            
        except Exception as e:
            print(f"Error parsing question: {e}")
            continue
    
    return questions

def fetch_page(page_num):
    """Fetch a single page from free-braindumps.com"""
    url = BASE_URL.format(page_num)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def load_existing_questions():
    """Load existing questions from file"""
    existing = []
    
    if EXISTING_QUESTIONS_FILE.exists():
        with open(EXISTING_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse existing questions
        q_blocks = re.split(r'---\nQ#:', content)
        
        for i, block in enumerate(q_blocks):
            if i == 0:
                # First block starts with Q#: 
                block = block.strip()
                if block.startswith('Q#:'):
                    block = block[4:]
            
            # Extract question text (first line after number)
            lines = block.strip().split('\n')
            if lines:
                q_num_match = re.search(r'(\d+)', lines[0])
                if q_num_match:
                    q_num = int(q_num_match.group(1))
                    existing.append(q_num)
    
    return set(existing)

def normalize_text(text):
    """Normalize text for comparison"""
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_duplicate(new_q, existing_questions, existing_texts):
    """Check if question is a duplicate"""
    # Check by question text similarity
    norm_new = normalize_text(new_q['question'])
    
    for existing_text in existing_texts:
        norm_existing = normalize_text(existing_text)
        
        # Simple similarity check
        if norm_new == norm_existing:
            return True
        
        # Check if one contains the other
        if len(norm_new) > 20 and len(norm_existing) > 20:
            if norm_new[:50] in norm_existing or norm_existing[:50] in norm_new:
                return True
    
    return False

def format_question_for_output(q, start_id):
    """Format question for output file"""
    # Map correct answer indices to letters
    answer_letters = [chr(65 + i) for i in q['correct_answers']]
    answer_str = ','.join(answer_letters) if len(answer_letters) > 1 else answer_letters[0]
    
    output = f"""Q#: {start_id}
{q['question']}
{chr(10).join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(q['options'])])}
Answer: {answer_str}
Explanation: {q['explanation']}
---"""
    return output

def main():
    print(f"Fetching pages {START_PAGE}-{END_PAGE} from free-braindumps.com...")
    
    # Load existing questions
    existing_q_nums = load_existing_questions()
    print(f"Found {len(existing_q_nums)} existing questions")
    
    # Track existing question texts for deduplication
    existing_texts = []
    if EXISTING_QUESTIONS_FILE.exists():
        with open(EXISTING_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract question texts
            for match in re.finditer(r'Q#:\s*\d+\n(.+?)(?:\n[A-D]\.)', content, re.DOTALL):
                existing_texts.append(match.group(1).strip())
    
    all_new_questions = []
    new_q_count = 0
    
    for page_num in range(START_PAGE, END_PAGE + 1):
        print(f"\nFetching page {page_num}...")
        
        html_content = fetch_page(page_num)
        if not html_content:
            print(f"Failed to fetch page {page_num}")
            continue
        
        # Parse questions
        questions = extract_questions_from_html(html_content, page_num)
        print(f"  Found {len(questions)} questions")
        
        # Filter duplicates
        for q in questions:
            if not is_duplicate(q, existing_q_nums, existing_texts):
                all_new_questions.append(q)
                existing_texts.append(q['question'])  # Add to existing for subsequent checks
                new_q_count += 1
        
        # Be polite to the server
        time.sleep(1)
    
    print(f"\nTotal new unique questions: {new_q_count}")
    
    # Save questions
    if all_new_questions:
        output_file = OUTPUT_DIR / "free-braindumps-new-questions.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, q in enumerate(all_new_questions):
                f.write(format_question_for_output(q, len(existing_q_nums) + i + 1))
                f.write('\n\n')
        
        print(f"Saved {new_q_count} new questions to {output_file}")
        
        # Also save as JSON for easier processing
        json_file = OUTPUT_DIR / "free-braindumps-new-questions.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_new_questions, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to {json_file}")
    else:
        print("No new questions found")

if __name__ == '__main__':
    main()
