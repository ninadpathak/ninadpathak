"""Publication metadata and permanent URL migration contracts."""
import json
import re
import unittest
from pathlib import Path

import frontmatter
try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent


class PostMetadataTests(unittest.TestCase):
    def test_each_published_essay_has_one_title_category_and_unique_slug_without_tags(self):
        categories = {row['slug'] for row in tomllib.loads((ROOT / 'config.toml').read_text())['content']['categories']}
        slugs = set()
        for path in (ROOT / 'content/posts').glob('*.md'):
            post = frontmatter.load(path)
            if post.get('status') != 'published':
                continue
            with self.subTest(path=path.name):
                self.assertNotIn('tags', post)
                self.assertNotIn('categories', post)
                self.assertIsInstance(post.get('category'), str)
                self.assertIn(post['category'], categories)
                self.assertIsInstance(post.get('title'), str)
                self.assertTrue(post['title'].strip())
                self.assertNotIn('\n', post['title'])
                self.assertRegex(post.get('slug', ''), r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                self.assertNotIn(post['slug'], categories)
                self.assertNotIn(post['slug'], slugs)
                slugs.add(post['slug'])
        self.assertTrue(slugs)

    def test_old_article_and_blog_urls_redirect_directly_to_current_canonical(self):
        redirects_path = ROOT / 'output/_redirects'
        if not redirects_path.exists():
            self.fail('Build the site before running URL migration tests.')
        rules = {}
        for line in redirects_path.read_text().splitlines():
            if line.startswith('/'):
                source, target, status = line.split()[:3]
                if source in rules:
                    self.assertEqual(rules[source], (target, status))
                rules[source] = (target, status)
        aliases = json.loads((ROOT / 'content/post-slug-aliases.json').read_text())
        for old, new in aliases.items():
            target = f'/articles/{new}/'
            if not (ROOT / 'output' / target.lstrip('/') / 'index.html').exists():
                continue
            self.assertNotIn(target, rules)
            for prefix in ('/articles/', '/blog/'):
                for suffix in ('', '/'):
                    self.assertEqual(rules[f'{prefix}{old}{suffix}'], (target, '301'))

    def test_related_reading_uses_category_without_rendering_tag_chips(self):
        posts = {}
        for path in (ROOT / 'content/posts').glob('*.md'):
            post = frontmatter.load(path)
            if post.get('status') == 'published':
                posts[post['slug']] = post['category']
        for slug, category in posts.items():
            html = (ROOT / 'output/articles' / slug / 'index.html').read_text()
            self.assertNotIn('class="post-tags"', html)
            self.assertIn(f'href="/articles/{category}/" class="tag"', html)
            related = re.search(r'<section class="post-related".*?</section>', html, re.S)
            self.assertIsNotNone(related)
            self.assertEqual(len(re.findall(r"<h1(?:\s|>)", html)), 1)
            if related:
                for target in re.findall(r'href="/articles/([^/]+)/"', related.group()):
                    self.assertEqual(posts[target], category)
