# Developer documentation style guide

Use this template to make product names, UI labels, code, and release language consistent across your docs. Replace every bracketed value before you publish.

## 1. Product names and terminology

| Concept | Approved term | Avoid | Definition | Owner | Last verified |
| --- | --- | --- | --- | --- | --- |
| [primary product] | [approved product name] | [old name, shorthand] | [one-sentence definition] | [team] | [YYYY-MM-DD] |
| [user role] | [approved role] | [ambiguous alternative] | [permission or responsibility] | [team] | [YYYY-MM-DD] |
| [feature] | [approved feature name] | [deprecated name] | [what it does] | [team] | [YYYY-MM-DD] |

Rules:

- Use the approved term after defining it once.
- Add a deprecated term only when readers will still encounter it in an interface, error, migration, or API.
- Link to the page that owns a term whose definition needs more than one sentence.

## 2. Voice, headings, and procedures

Write for the action the reader needs to complete. State the expected result before background that does not change the next step.

| Content type | Required shape | Completion signal |
| --- | --- | --- |
| Tutorial | Starting state, ordered path, result | A working command, response, or screen state |
| How-to | Known starting state, bounded change | The changed behavior is visible |
| Reference | Exact name, type, default, constraint | The reader can resolve the stable question |
| Troubleshooting | Symptom, diagnostic, cause, recovery | The failure is resolved or safely escalated |

Use sentence-case headings that name a task or a subject. Keep one page responsible for one reader question, then link to prerequisite, reference, or recovery pages.

## 3. Code and command examples

Record the environment that produced each example.

| Field | Value |
| --- | --- |
| Runtime and version | [for example, Python 3.13.5] |
| Package and version | [for example, requests 2.32.3] |
| Operating system and shell | [for example, Ubuntu 24.04 and Bash] |
| Starting state | [required files, access, or configuration] |
| Expected result | [response, exit code, file, or screen state] |
| Failure boundary | [what invalidates this example] |

```bash
# Run from: [working directory]
# Requires: [access, environment variables, or local service]
[copyable command]
```

Explain what the command changes and show the output or state that proves it worked. Do not publish a snippet that depends on hidden files, credentials, or global packages.

## 4. UI references and release checks

Use the label visible in the released interface. Describe the reader goal first when a control name alone does not explain the outcome.

| UI reference | Approved wording | Verification source | Last verified |
| --- | --- | --- | --- |
| [control or setting] | [exact visible label] | [release URL, build, or screenshot] | [YYYY-MM-DD] |
| [dialog or menu] | [exact visible label] | [release URL, build, or screenshot] | [YYYY-MM-DD] |

Before release, confirm:

- [ ] Every new product name appears in the terminology table.
- [ ] Every command has a starting state and expected result.
- [ ] Every UI label matches the released interface.
- [ ] Deprecated terms have a migration or compatibility reason.
- [ ] A named owner knows what product change triggers review.
