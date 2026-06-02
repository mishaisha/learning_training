#!/usr/bin/env python3
"""
Script to add explanations from test files to questions with empty explanations in the HTML file.
"""
import re
import json
from pathlib import Path

def extract_questions_from_html(html_file):
    """Extract questions from HTML file."""
    questions = []
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the ALL_QUESTIONS array
    match = re.search(r'const ALL_QUESTIONS = \[(.*?)\];', content, re.DOTALL)
    if not match:
        return questions
    
    questions_text = match.group(1)
    
    # Extract each question
    question_pattern = r'\{id:(\d+),domain:"([^"]*)",difficulty:"([^"]*)",type:"([^"]*)",question:"([^"]*)",options:\[(.*?)\],answer:(.*?),explanation:"([^"]*)"'
    
    for match in re.finditer(question_pattern, questions_text):
        q_id = int(match.group(1))
        domain = match.group(2)
        difficulty = match.group(3)
        q_type = match.group(4)
        question = match.group(5)
        options = match.group(6)
        answer = match.group(7)
        explanation = match.group(8)
        
        questions.append({
            'id': q_id,
            'domain': domain,
            'difficulty': difficulty,
            'type': q_type,
            'question': question,
            'options': options,
            'answer': answer,
            'explanation': explanation
        })
    
    return questions

def extract_explanations_from_test_files(test_files):
    """Extract explanations from test files."""
    explanations = []
    
    for file_path in test_files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            # Split by "Question" headers
            questions = re.split(r'Question \d+', content)
            
            for i, q_text in enumerate(questions[1:], 1):  # Skip first empty split
                # Extract question text
                lines = q_text.strip().split('\n')
                if len(lines) < 2:
                    continue
                
                # Find the question text (first few lines after "Correct/Incorrect")
                question_lines = []
                for line in lines[1:]:
                    if line.startswith('Your answer') or line.startswith('Your selection'):
                        continue
                    if line.startswith('Overall explanation'):
                        break
                    question_lines.append(line)
                
                question_text = ' '.join(question_lines[:3])  # Take first 3 lines as question
                
                # Extract explanation
                explanation_match = re.search(r'Overall explanation\s*\n.*?\n(.*?)(?:\n(?:Incorrect options|Reference|References|Domain|$))', q_text, re.DOTALL)
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                    # Clean up explanation
                    explanation = re.sub(r'\s+', ' ', explanation)
                    explanations.append({
                        'question': question_text,
                        'explanation': explanation
                    })
            
            print(f"  Found {len(questions)-1} questions")
        except Exception as e:
            print(f"  Error: {e}")
    
    return explanations

def normalize_text(text):
    """Normalize text for comparison."""
    # Remove special characters and normalize whitespace
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

def match_questions(html_questions, test_explanations):
    """Match questions from HTML with explanations from test files."""
    matches = []
    
    for html_q in html_questions:
        if html_q['explanation']:  # Skip questions that already have explanations
            continue
        
        # Normalize the question text
        html_q_normalized = normalize_text(html_q['question'])
        
        # Find matching explanation in test files
        for test_q in test_explanations:
            test_q_normalized = normalize_text(test_q['question'])
            
            # Check if questions match (using first 100 characters for partial matching)
            if html_q_normalized[:100] in test_q_normalized or test_q_normalized[:100] in html_q_normalized:
                matches.append({
                    'id': html_q['id'],
                    'explanation': test_q['explanation']
                })
                break
    
    return matches

def main():
    # Test files
    test_files = [
        'Files/Test2.txt',
        'Files/test3.txt', 
        'Files/test4.txt'
    ]
    
    # Extract questions from HTML
    print("Extracting questions from HTML...")
    html_questions = extract_questions_from_html('AWS_AIF_C01_Learning_Tool.html')
    print(f"Found {len(html_questions)} questions in HTML")
    
    # Count questions with empty explanations
    empty_explanations = [q for q in html_questions if not q['explanation']]
    print(f"Found {len(empty_explanations)} questions with empty explanations")
    
    # Extract explanations from test files
    print("\nExtracting explanations from test files...")
    test_explanations = extract_explanations_from_test_files(test_files)
    print(f"Found {len(test_explanations)} explanations in test files")
    
    # Match questions
    print("\nMatching questions...")
    matches = match_questions(html_questions, test_explanations)
    print(f"Found {len(matches)} matches")
    
    # Save matches to a file
    with open('Files/matched_explanations.json', 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    
    print("Matches saved to Files/matched_explanations.json")
    
    # Print some examples
    if matches:
        print("\nExample matches:")
        for match in matches[:5]:
            print(f"  ID {match['id']}: {match['explanation'][:100]}...")

if __name__ == '__main__':
    main()