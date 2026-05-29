#!/usr/bin/env python3
"""
Try to extract more questions from additional sources
"""

import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path

OUTPUT_DIR = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped")

def fetch_jwalsh_repo():
    """Fetch all practice tests from jwalsh/aif-c01 repo"""
    base_url = "https://raw.githubusercontent.com/jwalsh/aif-c01/main/practice-tests/"
    all_questions = []
    
    # Try to find all practice test files
    for i in range(1, 20):  # Try up to 20 files
        filename = f'aif-c01-practice-{i:02d}.org'
        url = base_url + filename
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                questions = parse_org_questions(response.text)
                all_questions.extend(questions)
                print(f"  {filename}: {len(questions)} questions")
            else:
                break  # No more files
        except Exception as e:
            print(f"  {filename}: Error - {e}")
            break
    
    return all_questions

def parse_org_questions(text):
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
                    'source': 'jwalsh/aif-c01',
                    'question': question_text,
                    'options': options,
                    'correct_answers': [correct_idx],
                    'explanation': explanation
                }
                questions.append(question)
        
        except Exception as e:
            continue
    
    return questions

def fetch_khanhvu_repo():
    """Fetch from khanhvu/aws-ai-practitioner"""
    url = "https://raw.githubusercontent.com/khanhvu/aws-ai-practitioner/main/README.md"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse for questions
            questions = []
            # Look for question patterns
            q_pattern = r'Question \d+: (.+?)(?:\n|$)'
            for match in re.finditer(q_pattern, response.text):
                questions.append({
                    'source': 'khanhvu/aws-ai-practitioner',
                    'question': match.group(1),
                    'options': [],  # Need to parse options
                    'correct_answers': [],
                    'explanation': ''
                })
            return questions
    except Exception as e:
        print(f"Error fetching khanhvu repo: {e}")
    
    return []

def main():
    print("Fetching additional questions from more sources...")
    
    # Try jwalsh repo (more files)
    print("\n1. jwalsh/aif-c01 repo:")
    jwalsh_questions = fetch_jwalsh_repo()
    print(f"   Total: {len(jwalsh_questions)} questions")
    
    # Try other repos
    print("\n2. Other repos:")
    other_questions = fetch_khanhvu_repo()
    print(f"   Total: {len(other_questions)} questions")
    
    # Combine all questions
    all_questions = jwalsh_questions + other_questions
    
    # Load existing questions for deduplication
    existing_file = OUTPUT_DIR / "additional_questions.json"
    if existing_file.exists():
        import json
        with open(existing_file, 'r') as f:
            existing_questions = json.load(f)
        
        # Deduplicate
        existing_texts = [q['question'].lower() for q in existing_questions]
        new_questions = [q for q in all_questions if q['question'].lower() not in existing_texts]
        
        print(f"\nNew unique questions: {len(new_questions)}")
        
        # Save new questions
        if new_questions:
            output_file = OUTPUT_DIR / "additional_questions_v2.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(new_questions, f, indent=2, ensure_ascii=False)
            print(f"Saved to {output_file}")
    
    return all_questions

if __name__ == '__main__':
    main()
