#!/usr/bin/env python3
"""
Add additional questions to the HTML tool
"""

import json
import re
from pathlib import Path

# Paths
HTML_FILE = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/AWS_AIF_C01_Learning_Tool.html")
QUESTIONS_FILE = Path("/Users/nehasinghal/Documents/AWS_Learning/aws_aif/scraped/additional_questions.json")

def load_questions():
    """Load questions from JSON file"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_question(q, qid):
    """Format question for HTML tool"""
    # Map domain to one of the existing domains
    domain_map = {
        'jwalsh/aif-c01': 'Fundamentals of AI and ML'
    }
    domain = domain_map.get(q.get('source', ''), 'Fundamentals of AI and ML')
    
    # Determine difficulty based on question content
    difficulty = 'MEDIUM'
    if any(word in q['question'].lower() for word in ['what is', 'which of the following', 'primary']):
        difficulty = 'EASY'
    
    # Format options
    options = q['options']
    if len(options) > 4:
        options = options[:4]
    
    # Format answer
    answer = q['correct_answers'][0] if q['correct_answers'] else 0
    
    # Escape special characters in strings
    def escape_js_string(s):
        # Escape backslashes
        s = s.replace('\\', '\\\\')
        # Escape double quotes
        s = s.replace('"', '\\"')
        # Escape newlines
        s = s.replace('\n', '\\n')
        # Escape carriage returns
        s = s.replace('\r', '\\r')
        # Escape tabs
        s = s.replace('\t', '\\t')
        return s
    
    # Format question string
    question_str = escape_js_string(q['question'])
    options_str = ','.join([f'"{escape_js_string(opt)}"' for opt in options])
    explanation_str = escape_js_string(q.get('explanation', ''))
    
    # Format as JavaScript object
    js_question = f'{{id:{qid},domain:"{domain}",difficulty:"{difficulty}",type:"mcq",question:"{question_str}",options:[{options_str}],answer:{answer},explanation:"{explanation_str}"}}'
    
    return js_question

def update_html(new_questions):
    """Update HTML file with new questions"""
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the end of ALL_QUESTIONS array
    # Look for the pattern: ];
    # after line 1168
    lines = content.split('\n')
    insert_line = None
    
    for i, line in enumerate(lines):
        if line.strip() == '];' and i > 1100:  # After ALL_QUESTIONS
            insert_line = i
            break
    
    if insert_line is None:
        print("Could not find insertion point")
        return False
    
    # Get current max ID
    id_pattern = r'\{id:(\d+),'
    ids = [int(m) for m in re.findall(id_pattern, content)]
    max_id = max(ids) if ids else 0
    
    # Format new questions
    formatted_questions = []
    for i, q in enumerate(new_questions):
        qid = max_id + i + 1
        formatted = format_question(q, qid)
        formatted_questions.append(formatted)
    
    # Insert new questions
    new_lines = lines[:insert_line]
    for q in formatted_questions:
        new_lines.append(q + ',')
    new_lines.extend(lines[insert_line:])
    
    # Update badge count
    content = '\n'.join(new_lines)
    
    # Update the badge in header
    total_questions = len(ids) + len(new_questions)
    content = re.sub(
        r'<span class="exam-badge">\d+ Q</span>',
        f'<span class="exam-badge">{total_questions} Q</span>',
        content
    )
    
    # Write updated content
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Added {len(new_questions)} questions to HTML tool")
    print(f"Total questions now: {total_questions}")
    return True

def main():
    print("Adding additional questions to HTML tool...")
    
    # Load questions
    questions = load_questions()
    print(f"Loaded {len(questions)} questions from JSON")
    
    # Update HTML
    if update_html(questions):
        print("\nSuccess! Questions added to HTML tool.")
    else:
        print("\nFailed to update HTML tool.")

if __name__ == '__main__':
    main()
