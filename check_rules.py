import re
import sys

files = [
    'content/posts/technical-writing-for-ai-products-the-new-rules.md',
    'content/posts/developer-onboarding-docs-what-works-what-doesnt.md',
    'content/posts/how-to-write-a-technical-tutorial-that-actually-teaches.md'
]

banned_starters = ['in', 'this', 'by', 'finally', 'most', 'ever']

def check_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for emdashes
    emdashes = re.findall(r'—', content)
    if emdashes:
        print(f"Found {len(emdashes)} emdashes in {file_path}")

    # Check for banned starters
    # Split content by sentences (roughly)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    for s in sentences:
        s = s.strip()
        if not s: continue
        # Ignore markdown headers, lists, etc.
        if s.startswith('#') or s.startswith('-') or s.startswith('*') or s.startswith('1.'):
            continue
        
        words = s.split()
        if words:
            first_word = words[0].lower().strip('*"\'_')
            if first_word in banned_starters:
                print(f"Banned starter '{first_word}' in {file_path}: {s[:100]}...")

for f in files:
    check_file(f)
