# NinadPathak.com content calendar

This is a local-only, Docker-hosted view of the canonical 90-release plan in
`planning/documentation-authority-plan.md`.

Open `http://ninadplan.localhost` after the container is running. Status changes are
stored in the browser's local storage and do not publish or modify website content.

Start or rebuild:

```sh
docker compose up -d --build
```

Stop without deleting the container:

```sh
docker compose stop
```
