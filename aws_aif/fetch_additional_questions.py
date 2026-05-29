#!/usr/bin/env python3
"""
Fetch AWS AIF-C01 questions from multiple free sources:
1. GitHub repos (jwalsh/aif-c01, kananinirav, khasky)
2. Web sources (masteryexamprep, tutorialsdojo, examos, examcert, certempire)
"""

import requests
import re
import json
from bs4 import BeautifulSoup
from pathlib import Path

OUTPUT_DIR = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped")

def fetch_github_repo_questions():
    """Fetch questions from GitHub repositories"""
    repos = [
        {
            'name': 'jwalsh/aif-c01',
            'base_url': 'https://raw.githubusercontent.com/jwalsh/aif-c01/main/practice-tests/',
            'files': [f'aif-c01-practice-{i:02d}.org' for i in range(1, 6)]
        },
        {
            'name': 'kananinirav/aws-certified-ai-practitioner-study-notes',
            'base_url': 'https://raw.githubusercontent.com/kananinirav/aws-certified-ai-practitioner-study-notes/master/',
            'files': ['practice-test/questions.md']
        }
    ]
    
    all_questions = []
    
    for repo in repos:
        print(f"\nFetching from {repo['name']}...")
        
        for filename in repo['files']:
            url = repo['base_url'] + filename
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    questions = parse_org_questions(response.text, repo['name'])
                    all_questions.extend(questions)
                    print(f"  {filename}: {len(questions)} questions")
                else:
                    print(f"  {filename}: Not found")
            except Exception as e:
                print(f"  {filename}: Error - {e}")
    
    return all_questions

def parse_org_questions(text, source):
    """Parse questions from org-mode format"""
    questions = []
    
    # Split by question markers
    q_blocks = re.split(r'\*\* Question \d+:', text)
    
    for i, block in enumerate(q_blocks[1:], 1):
        try:
            # Extract question text
            q_match = re.search(r'^(.+?)(?:\n|$)', block)
            if not q_match:
                continue
            
            question_text = q_match.group(1).strip()
            
            # Extract answer from properties
            answer_match = re.search(r':ANSWER:\s*(.+?)$', block, re.MULTILINE)
            if not answer_match:
                continue
            
            correct_answer_text = answer_match.group(1).strip()
            
            # Extract explanation
            expl_match = re.search(r':EXPLANATION:\s*(.+?)$', block, re.MULTILINE)
            explanation = expl_match.group(1).strip() if expl_match else ""
            
            # Extract options
            options = []
            correct_idx = 0
            
            for opt_match in re.finditer(r'- \[([ X])\]\s*(.+)$', block, re.MULTILINE):
                marker = opt_match.group(1)
                option_text = opt_match.group(2).strip()
                options.append(option_text)
                
                if marker == 'X':
                    correct_idx = len(options) - 1
            
            if len(options) >= 2:
                question = {
                    'source': source,
                    'question': question_text,
                    'options': options,
                    'correct_answers': [correct_idx],
                    'explanation': explanation
                }
                questions.append(question)
        
        except Exception as e:
            print(f"  Error parsing question {i}: {e}")
            continue
    
    return questions

def fetch_web_questions():
    """Fetch questions from web sources"""
    sources = [
        {
            'name': 'certempire',
            'url': 'https://certempire.com/practice-tests/free-aif-c01-practice-questions/'
        },
        {
            'name': 'examos',
            'url': 'https://examos.io/aif-c01-practice-questions'
        }
    ]
    
    all_questions = []
    
    for source in sources:
        print(f"\nFetching from {source['name']}...")
        try:
            response = requests.get(source['url'], timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                questions = parse_web_questions(response.text, source['name'])
                all_questions.extend(questions)
                print(f"  Found {len(questions)} questions")
            else:
                print(f"  Failed: {response.status_code}")
        
        except Exception as e:
            print(f"  Error: {e}")
    
    return all_questions

def parse_web_questions(html_content, source):
    """Parse questions from web pages"""
    soup = BeautifulSoup(html_content, 'html.parser')
    questions = []
    
    # Try different patterns based on source
    if source == 'certempire':
        # Look for question blocks
        q_blocks = soup.find_all(['div', 'p'], string=re.compile(r'^Q:\s*\d+'))
        
        for block in q_blocks:
            try:
                # Extract question number
                q_num_match = re.search(r'Q:\s*(\d+)', block.get_text())
                if not q_num_match:
                    continue
                
                # Get next sibling elements for question text and options
                next_elem = block.find_next_sibling()
                if not next_elem:
                    continue
                
                # Extract question text
                question_text = next_elem.get_text(strip=True)
                
                # Get options
                options = []
                correct_answers = []
                
                # Look for option elements
                for opt in next_elem.find_all(['li', 'div'], class_=re.compile(r'option|answer')):
                    opt_text = opt.get_text(strip=True)
                    if opt_text:
                        options.append(opt_text)
                
                # Try to find correct answer from explanation
                expl_elem = next_elem.find_next_sibling()
                if expl_elem:
                    expl_text = expl_elem.get_text(strip=True)
                    # Look for answer indicator
                    answer_match = re.search(r'Answer:\s*([A-D])', expl_text)
                    if answer_match:
                        correct_answers = [ord(answer_match.group(1)) - ord('A')]
                
                if len(options) >= 2 and correct_answers:
                    question = {
                        'source': source,
                        'question': question_text,
                        'options': options[:4],  # Limit to 4 options
                        'correct_answers': correct_answers,
                        'explanation': expl_text if expl_elem else ""
                    }
                    questions.append(question)
            
            except Exception as e:
                continue
    
    return questions

def normalize_text(text):
    """Normalize text for comparison"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_duplicate(new_q, existing_texts):
    """Check if question is a duplicate"""
    norm_new = normalize_text(new_q['question'])
    
    for existing_text in existing_texts:
        norm_existing = normalize_text(existing_text)
        
        if norm_new == norm_existing:
            return True
        
        if len(norm_new) > 30 and len(norm_existing) > 30:
            if norm_new[:50] in norm_existing or norm_existing[:50] in norm_new:
                return True
    
    return False

def main():
    print("=" * 60)
    print("AWS AIF-C01 Question Fetcher")
    print("=" * 60)
    
    # Load existing questions for deduplication
    existing_file = OUTPUT_DIR / "free-braindumps-questions.txt"
    existing_texts = []
    
    if existing_file.exists():
        with open(existing_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract question texts
            for match in re.finditer(r'Q#:\s*\d+\n(.+?)(?:\n[A-D]\.)', content, re.DOTALL):
                existing_texts.append(match.group(1).strip())
        print(f"Loaded {len(existing_texts)} existing questions for deduplication")
    
    # Fetch from GitHub
    github_questions = fetch_github_repo_questions()
    
    # Fetch from web
    web_questions = fetch_web_questions()
    
    # Combine all questions
    all_questions = github_questions + web_questions
    print(f"\nTotal questions fetched: {len(all_questions)}")
    
    # Deduplicate
    new_questions = []
    for q in all_questions:
        if not is_duplicate(q, existing_texts):
            new_questions.append(q)
            existing_texts.append(q['question'])
    
    print(f"New unique questions: {len(new_questions)}")
    
    # Save questions
    if new_questions:
        output_file = OUTPUT_DIR / "additional_questions.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, q in enumerate(new_questions):
                answer_letters = [chr(65 + i) for i in q['correct_answers']]
                answer_str = ','.join(answer_letters) if len(answer_letters) > 1 else answer_letters[0]
                
                f.write(f"Q#: {i+1} (source: {q['source']})\n")
                f.write(f"{q['question']}\n")
                for j, opt in enumerate(q['options']):
                    f.write(f"{chr(65+j)}. {opt}\n")
                f.write(f"Answer: {answer_str}\n")
                if q['explanation']:
                    f.write(f"Explanation: {q['explanation'][:200]}...\n")
                f.write("\n---\n\n")
        
        print(f"Saved {len(new_questions)} questions to {output_file}")
        
        # Also save as JSON
        json_file = OUTPUT_DIR / "additional_questions.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(new_questions, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to {json_file}")
    else:
        print("No new questions found")

if __name__ == '__main__':
    main()
