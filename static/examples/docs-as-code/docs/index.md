# statuscount

`statuscount` is a command-line tool that counts the HTTP status codes in a web server's access log. It is one Python file with no dependencies, and it needs Python 3.9 or later.

## Start here

- [Count the status codes in a log](usage.md)
- [Count errors only](usage.md#count-errors-only)
- [Fix a "cannot read" error](usage.md#fix-a-cannot-read-error)

## What the log has to look like

The tool reads the [Common Log Format](https://httpd.apache.org/docs/2.4/logs.html#common) that Apache documents, where the status code follows the quoted request line. A line with no quoted request is skipped.
