# Documentation accessibility checker

Run the checker against rendered HTML, not source Markdown.

```bash
python3 check_documentation_accessibility.py rendered-page.html
```

The checker flags missing `alt` attributes, vague link text, heading-level jumps, tables without header cells, and code elements that do not declare a language class. It does not test keyboard behavior, contrast, zoom reflow, or screen-reader output.
