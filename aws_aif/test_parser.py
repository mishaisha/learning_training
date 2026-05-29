#!/usr/bin/env python3
"""
Test parser on existing HTML files (pg17-pg21) to verify it works correctly
"""

import re
import html
from bs4 import BeautifulSoup
from pathlib import Path

def clean_html(text):
    """Remove HTML tags and decode entities"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_questions_from_html(html_content, filename):
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
                'filename': filename,
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

def main():
    # Test on existing HTML files
    files_dir = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/Files")
    html_files = ['pg17.html', 'pg18.html', 'pg19.html', 'pg21.html']
    
    all_questions = []
    
    for filename in html_files:
        filepath = files_dir / filename
        if not filepath.exists():
            print(f"File not found: {filepath}")
            continue
        
        print(f"\nParsing {filename}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        questions = extract_questions_from_html(html_content, filename)
        print(f"  Found {len(questions)} questions")
        
        for q in questions:
            print(f"  Q{q['id']}: {q['question'][:80]}...")
            print(f"         Options: {len(q['options'])}, Correct: {q['correct_answers']}")
        
        all_questions.extend(questions)
    
    print(f"\nTotal questions parsed: {len(all_questions)}")
    
    # Save to test file
    output_file = files_dir / "test_parsed_questions.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for q in all_questions:
            f.write(f"Q#: {q['id']} (from {q['filename']})\n")
            f.write(f"{q['question']}\n")
            for i, opt in enumerate(q['options']):
                marker = '*' if i in q['correct_answers'] else ' '
                f.write(f"{marker} {chr(65+i)}. {opt}\n")
            f.write(f"Answer: {','.join([chr(65+i) for i in q['correct_answers']])}\n")
            if q['explanation']:
                f.write(f"Explanation: {q['explanation'][:200]}...\n")
            f.write("\n---\n\n")
    
    print(f"Saved parsed questions to {output_file}")

if __name__ == '__main__':
    main()
