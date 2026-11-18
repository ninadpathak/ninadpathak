# The repro behind the process page

The terminal on `/technical-writing-process/` shows commands that were run, with the output they printed. This folder is that run.

- `plurals.mjs` renders one cart line through react-i18next for a language and compares the plural key i18next used with the one `Intl.PluralRules` asks for.
- `locales/` holds English and an Arabic file with only `_one` and `_other`. i18next raises no error for it and falls back to `_other` for 3 and 11, which Arabic counts as `few` and `many`.
- `locales-fixed/` adds the missing Arabic forms.
- `transcript.txt` is the output of the three commands, captured on 18 November 2026 with i18next 27.1.5, react-i18next 18.0.2 and React 19.3.1.

To run it again:

```bash
npm install react react-dom i18next react-i18next
node plurals.mjs en
node plurals.mjs ar
node plurals.mjs ar locales-fixed
```

`tests/test_process_page.py` fails if a terminal line on the page is not in `transcript.txt`.
