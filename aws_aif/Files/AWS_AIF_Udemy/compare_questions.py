#!/usr/bin/env python3
"""
Fast comparison: 260 Udemy questions vs HTML tool's ALL_QUESTIONS.
Uses first-100-char matching + keyword overlap (no SequenceMatcher).
"""

import json
import re
import sys
from collections import defaultdict

# ── Load Udemy questions ──────────────────────────────────────────────────────
with open('/Users/nehasinghal/Desktop/AWS_AIF_Udemy/all_parsed_questions.json') as f:
    udemy_questions = json.load(f)

print(f"Loaded {len(udemy_questions)} Udemy questions")

# ── Load HTML tool questions ──────────────────────────────────────────────────
with open('/Users/nehasinghal/Documents/AWS_Learning/aws_aif/AWS_AIF_C01_Learning_Tool.html') as f:
    html_content = f.read()

# Extract ALL_QUESTIONS array
start_marker = "const ALL_QUESTIONS = ["
start_idx = html_content.find(start_marker)
array_start = start_idx + len(start_marker)

depth = 1
pos = array_start
while depth > 0 and pos < len(html_content):
    if html_content[pos] == '[':
        depth += 1
    elif html_content[pos] == ']':
        depth -= 1
    pos += 1

array_str = html_content[array_start:pos-1].strip()
if array_str.endswith(','):
    array_str = array_str[:-1]
array_str = '[' + array_str + ']'

# Parse HTML questions
html_questions = []
q_blocks = re.findall(r'\{id:\d+.*?\}(?=,\s*\{id:|\s*$)', array_str, re.DOTALL)

for block in q_blocks:
    try:
        id_match = re.search(r'id:(\d+)', block)
        domain_match = re.search(r'domain:"([^"]*)"', block)
        question_match = re.search(r'question:"((?:[^"\\]|\\.)*)"', block)
        explanation_match = re.search(r'explanation:"((?:[^"\\]|\\.)*)"', block)
        
        if all([id_match, domain_match, question_match]):
            q = {
                'id': int(id_match.group(1)),
                'domain': domain_match.group(1),
                'question': question_match.group(1).replace('\\"', '"').replace('\\n', '\n'),
                'explanation': explanation_match.group(1).replace('\\"', '"').replace('\\n', '\n') if explanation_match else ''
            }
            html_questions.append(q)
    except:
        continue

print(f"Parsed {len(html_questions)} HTML questions")

# ── Fast matching functions ───────────────────────────────────────────────────
def normalize(text):
    """Normalize: lowercase, collapse whitespace, strip."""
    text = re.sub(r'\s+', ' ', text.strip().lower())
    return text

def first_n(text, n=100):
    """First n non-space chars."""
    return re.sub(r'\s+', '', text.lower())[:n]

def extract_keywords(text):
    """Extract meaningful keywords (4+ chars, not stopwords)."""
    stopwords = {
        'which', 'what', 'how', 'that', 'this', 'with', 'for', 'from',
        'have', 'been', 'will', 'would', 'should', 'could', 'need',
        'want', 'using', 'based', 'company', 'team', 'model', 'data',
        'use', 'case', 'most', 'best', 'approach', 'solution', 'service',
        'feature', 'application', 'system', 'process', 'required',
        'following', 'statement', 'select', 'true', 'false', 'about',
        'their', 'into', 'must', 'when', 'does', 'each', 'also',
        'such', 'than', 'only', 'other', 'more', 'some', 'very',
        'make', 'like', 'over', 'after', 'before', 'between', 'under',
        'while', 'during', 'through', 'where', 'there', 'then',
        'these', 'those', 'being', 'both', 'each', 'same', 'they',
        'them', 'your', 'many', 'much', 'well', 'back', 'even',
        'still', 'just', 'first', 'last', 'long', 'great', 'high',
        'small', 'large', 'next', 'early', 'young', 'important',
        'few', 'public', 'bad', 'old', 'different', 'big', 'family',
        'system', 'every', 'found', 'go', 'our', 'out', 'day',
        'had', 'has', 'his', 'her', 'its', 'may', 'new', 'now',
        'old', 'see', 'way', 'who', 'did', 'get', 'let', 'say',
        'she', 'too', 'use', 'adit', 'make', 'sure'
    }
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    return set(w for w in words if w not in stopwords)

# Precompute HTML question data
html_first100 = [first_n(q['question'], 100) for q in html_questions]
html_keywords = [extract_keywords(q['question']) for q in html_questions]

# ── Compare each Udemy question ──────────────────────────────────────────────
covered = []
uncovered = []
uncovered_by_domain = defaultdict(list)

for uq in udemy_questions:
    uq_text = uq.get('question', '')
    uq_first100 = first_n(uq_text, 100)
    uq_keywords = extract_keywords(uq_text)
    
    is_covered = False
    best_match_id = None
    best_score = 0
    
    for i, hq in enumerate(html_questions):
        # Method 1: First 100 chars exact match
        if uq_first100 == html_first100[i] and len(uq_first100) >= 60:
            is_covered = True
            best_match_id = hq['id']
            best_score = 1.0
            break
        
        # Method 2: First 100 chars high overlap (>80%)
        if len(uq_first100) >= 40 and len(html_first100[i]) >= 40:
            # Check if they share 80%+ of first-100 content
            shorter = min(len(uq_first100), len(html_first100[i]))
            matching = sum(1 for a, b in zip(uq_first100, html_first100[i]) if a == b)
            if matching / shorter >= 0.80:
                is_covered = True
                best_match_id = hq['id']
                best_score = 0.95
                break
        
        # Method 3: Keyword overlap
        if uq_keywords and html_keywords[i]:
            overlap = len(uq_keywords & html_keywords[i])
            smaller = min(len(uq_keywords), len(html_keywords[i]))
            if smaller > 0:
                kw_ratio = overlap / smaller
                if kw_ratio > best_score:
                    best_score = kw_ratio
                    best_match_id = hq['id']
        
        # If keyword overlap >= 60%, consider covered
        if best_score >= 0.60 and best_match_id:
            # But verify it's actually the same question topic
            # by checking if key domain-specific terms match
            overlap_set = uq_keywords & html_keywords[i]
            # Must share at least one AWS service name or technical concept
            has_tech_overlap = bool(overlap_set & {
                'amazon', 'bedrock', 'sagemaker', 'kendra', 'comprehend',
                'textract', 'transcribe', 'rekognition', 'personalize',
                'forecast', 'polly', 'lex', 's3', 'ec2', 'lambda',
                'kms', 'cloudtrail', 'guardrails', 'knowledge', 'bases',
                'agents', 'rag', 'llm', 'fine-tuning', 'pre-training',
                'inference', 'training', 'deploy', 'endpoint', 'pipeline',
                'monitor', 'clarify', 'experiments', 'feature', 'store',
                'registry', 'pipelines', 'wrangler', 'tuning'
            })
            if has_tech_overlap:
                is_covered = True
                break
    
    if is_covered:
        covered.append({
            'udemy_num': uq.get('question_number'),
            'udemy_text': uq_text[:120],
            'html_id': best_match_id,
            'score': best_score,
            'domain': uq.get('domain')
        })
    else:
        uncovered.append({
            'question_number': uq.get('question_number'),
            'question': uq_text,
            'domain': uq.get('domain'),
            'options': uq.get('options', []),
            'correct_option': uq.get('correct_option'),
            'test_number': uq.get('test_number')
        })
        uncovered_by_domain[uq.get('domain', 'Unknown')].append(uq.get('question_number'))

# ── Print Results ─────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("COMPREHENSIVE COMPARISON RESULTS")
print("="*80)

print(f"\nTotal Udemy questions compared:  {len(udemy_questions)}")
print(f"Total HTML tool questions:       {len(html_questions)}")
print(f"\nCOVERED (match in HTML tool):    {len(covered)}  ({len(covered)/len(udemy_questions)*100:.1f}%)")
print(f"NOT COVERED (no match):          {len(uncovered)}  ({len(uncovered)/len(udemy_questions)*100:.1f}%)")

print("\n" + "-"*80)
print("DOMAIN BREAKDOWN")
print("-"*80)

all_domains = sorted(set(q.get('domain', 'Unknown') for q in udemy_questions))
for domain in all_domains:
    total_in = sum(1 for q in udemy_questions if q.get('domain') == domain)
    uncov_in = len(uncovered_by_domain.get(domain, []))
    cov_in = total_in - uncov_in
    pct = (uncov_in / total_in * 100) if total_in > 0 else 0
    print(f"\n{domain}:")
    print(f"  Total: {total_in}  |  Covered: {cov_in}  |  NOT Covered: {uncov_in}  ({pct:.0f}%)")

print("\n" + "="*80)
print("ALL UNCOVERED QUESTIONS")
print("="*80)

for i, q in enumerate(uncovered, 1):
    print(f"\n{'─'*80}")
    print(f"[{i}/{len(uncovered)}] Q#{q['question_number']} (Test {q['test_number']})")
    print(f"Domain: {q['domain']}")
    print(f"Q: {q['question'][:250]}{'...' if len(q['question']) > 250 else ''}")
    print(f"Correct: {q['correct_option']}")

# Save JSON
results = {
    'summary': {
        'total_udemy': len(udemy_questions),
        'total_html': len(html_questions),
        'covered': len(covered),
        'uncovered': len(uncovered),
        'coverage_rate': f"{len(covered)/len(udemy_questions)*100:.1f}%"
    },
    'domain_breakdown': {},
    'uncovered_questions': uncovered
}
for domain in all_domains:
    total_in = sum(1 for q in udemy_questions if q.get('domain') == domain)
    uncov_in = len(uncovered_by_domain.get(domain, []))
    results['domain_breakdown'][domain] = {
        'total': total_in,
        'covered': total_in - uncov_in,
        'uncovered': uncov_in
    }

with open('/Users/nehasinghal/Desktop/AWS_AIF_Udemy/comparison_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to comparison_results.json")
