# Troubleshooting {{the product, feature or area}}

<!-- One entry per symptom, ordered by how often readers report each one. An entry has to make
     sense alone, because a reader lands on it from a search for the error text and reads nothing
     above it. Keep each Field: line. Check the page with:
     python3 check_troubleshooting_guide.py --filled guide.md -->

Applies to: {{the product, its version and the operating system the entries were reproduced on}}
Last reproduced: {{YYYY-MM-DD, the last time someone triggered every symptom and ran every fix}}

<!-- An entry heading in backticks is the error text, copied from the output. Cut a long message
     down to the part that stays the same for every reader, and drop anything that belongs to
     one reader, such as a table name or a path. A symptom that prints no message gets a plain
     heading that says what the reader sees. -->

## `{{the part of the error message that every reader sees}}`

Symptom:

```text
{{the command that fails and its output, pasted from a terminal}}
```

<!-- One ### per cause, the likeliest first. A reader whose output does not match
     "Your cause if" moves to the next cause, and after the last one to "Still stuck?". -->

### {{The first cause, in a few words}}

Why: {{one or two sentences on how this cause produces the symptom}}

Check:

```bash
{{a command that tells this cause from the others}}
```

Your cause if: {{the output that means this cause is the reader's}}

Fix:

```bash
{{the command that removes the cause, copied from a run that worked}}
```

Verify:

```bash
{{the command that failed in Symptom, or one that shows the result}}
```

Fixed when: {{the output the reader sees once the fix has worked}}

### {{The second cause, if the same symptom has one}}

Why: {{how this cause produces the same symptom}}

Check:

```bash
{{the command}}
```

Your cause if: {{the output that confirms it}}

Fix:

```bash
{{the command}}
```

Verify:

```bash
{{the command}}
```

Fixed when: {{the output after the fix}}

## {{A symptom with no error message, as the reader would describe it}}

Symptom:

```text
{{the commands and output that show the wrong behavior}}
```

### {{The cause, in a few words}}

Why: {{how this cause produces the symptom}}

Check:

```bash
{{the command}}
```

Your cause if: {{the output that confirms it}}

Fix:

```bash
{{the command}}
```

Verify:

```bash
{{the command}}
```

Fixed when: {{the output after the fix}}

## Still stuck?

Collect: {{the versions, command and output to copy before asking for help}}
Contact: {{where to send them, and what to search first}}
