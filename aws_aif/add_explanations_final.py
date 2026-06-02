#!/usr/bin/env python3
"""
Script to add matched explanations to the HTML file.
"""
import re
import json
from pathlib import Path

def add_explanations_to_html(html_file, matches_file, output_file):
    """Add explanations to the HTML file."""
    # Load matches
    with open(matches_file, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    # Create a dictionary of matches
    matches_dict = {match['id']: match['explanation'] for match in matches}
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the ALL_QUESTIONS array
    match = re.search(r'(const ALL_QUESTIONS = \[)(.*?)(\];)', content, re.DOTALL)
    if not match:
        print("Could not find ALL_QUESTIONS array")
        return
    
    questions_text = match.group(2)
    
    # Replace empty explanations with matched explanations
    def replace_explanation(match):
        full_match = match.group(0)
        q_id = int(match.group(1))
        if q_id in matches_dict:
            # Escape the explanation for JavaScript
            explanation = matches_dict[q_id]
            # Escape double quotes and backslashes
            explanation = explanation.replace('\\', '\\\\')
            explanation = explanation.replace('"', '\\"')
            # Replace the empty explanation with the new one
            return full_match.replace('explanation:""', f'explanation:"{explanation}"')
        return full_match
    
    # Pattern to match question IDs and their explanations
    pattern = r'id:(\d+),explanation:""'
    
    # Replace empty explanations
    new_questions_text = re.sub(pattern, replace_explanation, questions_text)
    
    # Reconstruct the HTML
    new_content = content[:match.start(2)] + new_questions_text + content[match.end(2):]
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added explanations to {len(matches_dict)} questions")
    print(f"Output saved to {output_file}")

def main():
    add_explanations_to_html(
        'AWS_AIF_C01_Learning_Tool.html',
        'Files/matched_explanations.json',
        'AWS_AIF_C01_Learning_Tool_with_explanations.html'
    )

if __name__ == '__main__':
    main()