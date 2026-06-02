#!/usr/bin/env python3
"""
Script to extract explanations from test files and add them to questions with empty explanations.
"""
import re
import json
from pathlib import Path

def extract_explanations_from_test_file(file_path):
    """Extract explanations from a test file."""
    explanations = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Question" headers
    questions = re.split(r'Question \d+', content)
    
    for i, q_text in enumerate(questions[1:], 1):  # Skip first empty split
        # Extract question text
        question_match = re.search(r'(?:Incorrect|Correct)\s*\n(.*?)(?:\n(?:Your answer|Your selection|The company|The developer|The data|A |An |Which|What|How|Why|In |For |Based|Consider|A company))', q_text, re.DOTALL)
        if not question_match:
            continue
        
        # Extract explanation
        explanation_match = re.search(r'Overall explanation\s*\n.*?\n(.*?)(?:\n(?:Incorrect options|Reference|References|Domain|$))', q_text, re.DOTALL)
        if explanation_match:
            explanation = explanation_match.group(1).strip()
            # Clean up explanation
            explanation = re.sub(r'\s+', ' ', explanation)
            explanation = explanation.replace('"', '\\"')
            explanations[i] = explanation
    
    return explanations

def extract_questions_and_explanations(file_path):
    """Extract questions and their explanations from a test file."""
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Question" headers
    questions = re.split(r'Question \d+', content)
    
    for i, q_text in enumerate(questions[1:], 1):  # Skip first empty split
        # Check if question is marked as correct or incorrect
        is_correct = 'Correct' in q_text.split('\n')[0] if q_text else False
        
        # Extract question text (first few lines after "Correct/Incorrect")
        lines = q_text.strip().split('\n')
        if len(lines) < 2:
            continue
            
        # Find the question text
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
            results.append({
                'question': question_text,
                'explanation': explanation,
                'is_correct': is_correct
            })
    
    return results

def main():
    # Test files
    test_files = [
        'Files/Test2.txt',
        'Files/test3.txt', 
        'Files/test4.txt'
    ]
    
    all_explanations = {}
    
    for file_path in test_files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            # Split by "Question" headers
            questions = re.split(r'Question \d+', content)
            
            for i, q_text in enumerate(questions[1:], 1):  # Skip first empty split
                # Extract explanation
                explanation_match = re.search(r'Overall explanation\s*\n.*?\n(.*?)(?:\n(?:Incorrect options|Reference|References|Domain|$))', q_text, re.DOTALL)
                if explanation_match:
                    explanation = explanation_match.group(1).strip()
                    # Clean up explanation
                    explanation = re.sub(r'\s+', ' ', explanation)
                    all_explanations[i] = explanation
            
            print(f"  Found {len(questions)-1} questions")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nTotal explanations found: {len(all_explanations)}")
    
    # Save explanations to a JSON file
    with open('Files/explanations.json', 'w', encoding='utf-8') as f:
        json.dump(all_explanations, f, indent=2, ensure_ascii=False)
    
    print("Explanations saved to Files/explanations.json")

if __name__ == '__main__':
    main()