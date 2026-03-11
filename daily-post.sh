#!/bin/bash
# Daily blog post publisher
# Run this every morning at 10am via cron:
#   0 10 * * * /Users/ninad/Development/NinadPathak/daily-post.sh >> /Users/ninad/Development/NinadPathak/planning/daily-log.txt 2>&1

REPO_DIR="/Users/ninad/Development/NinadPathak"
LOG="$REPO_DIR/planning/daily-log.txt"

echo "=== $(date) ===" >> "$LOG"
echo "Starting daily post..." >> "$LOG"

cd "$REPO_DIR" || exit 1

# Pull latest
git pull origin main >> "$LOG" 2>&1

# Ask Claude to write the next post
# Claude Code CLI: https://github.com/anthropics/claude-code
claude --print "Read /Users/ninad/Development/NinadPathak/planning/post-queue.md to find the next unwritten post. Check /Users/ninad/Development/NinadPathak/content/posts/ for all existing posts to determine which queue item comes next. Write that post following all rules in post-queue.md. Use the flyio-blog-writer skill's narrative_style_guide voice (professional, first-person, no profanity). Save it to /Users/ninad/Development/NinadPathak/content/posts/ with a slug-style filename. Then run: cd /Users/ninad/Development/NinadPathak && python3 build.py && git add content/posts/ output/ && git commit -m 'Daily post: [post title]' && git push origin main" >> "$LOG" 2>&1

echo "Done." >> "$LOG"
