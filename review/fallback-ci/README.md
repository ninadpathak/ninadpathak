# Kept-visual reveal: evidence

The two kept visuals (cosine-similarity, matryoshka-truncation) now post `{type: 'visual-ready'}` to the article once drawn. `static/js/main.js` reveals the frame when that message arrives (same origin, matching `contentWindow`), or when it finds `window.npVisualReady` already set. It no longer waits on the frame's `load` event. CI now runs `node tools/image-brand/fallbacks.mjs --check`.

`results.txt` comes from `reveal-test.mjs` running against a local build of `/articles/vector-embeddings/`. Each row reports both frames: `ready` (the frame was revealed), the frame's opacity, and whether the fallback drawing for the active theme loaded.

| Case | What it simulates | Result |
|---|---|---|
| normal, light and dark, 375 and 1366 | Ordinary load | Both frames revealed |
| blocked, light and dark | The iframe request is aborted | Frames stay transparent and the fallback shows |
| deferred-page-new | Page script runs 1.5 s after the frame's `load` event, as with Rocket Loader | Revealed |
| deferred-page-OLD-main | Same, with main.js from main | **Not revealed**: the old reveal checked the flag only at `load`, so this is the bug being fixed |
| slow-main | main.js arrives 3 s late, after the page has drawn and posted | Revealed through the flag |
| slow-main and deferred page | Both late | Revealed |

Run it with `OLD_MAIN_JS=<main.js from main> node review/fallback-ci/reveal-test.mjs` while serving `output/` on 127.0.0.1:8801.

`data-cfasync="false"` isn't needed. The handshake works whichever script runs first, and the site has no other `data-cfasync` usage.
