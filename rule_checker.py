import re
import os

files = [
    'content/posts/technical-writing-for-ai-products-the-new-rules.md',
    'content/posts/developer-onboarding-docs-what-works-what-doesnt.md',
    'content/posts/how-to-write-a-technical-tutorial-that-actually-teaches.md'
]

banned_starters = ['in', 'this', 'by', 'finally', 'most', 'ever']

def find_violations(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    print(f"--- Checking {file_path} ---")
    for i, line in enumerate(lines):
        line_num = i + 1
        # Check emdashes
        if '—' in line:
            print(f"[{line_num}] EMDASH: {line.strip()[:100]}")
        
        # Check starters
        # Simple split by sentence-like punctuation
        sentences = re.split(r'(?<=[.!?])\s+', line)
        for s in sentences:
            s = s.strip()
            if not s: continue
            words = s.split()
            if words:
                first_word = words[0].lower().strip('*"\'_')
                if first_word in banned_starters:
                    print(f"[{line_num}] BANNED STARTER '{first_word}': {s[:100]}")

for f in files:
    find_violations(f)
