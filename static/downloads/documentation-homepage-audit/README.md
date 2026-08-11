# Documentation homepage route audit

A documentation homepage should make a next move visible for a new user, a returning implementer, someone recovering from a failure, and someone exploring the product.

Run the included fixture:

```bash
python3 audit_homepage_routes.py example-homepage-routes.json
```

Create a JSON file with a `routes` array. Every route needs `job`, `label`, `url`, and `audience`. The auditor fails when one of the four route jobs is missing or when labels are duplicated.
