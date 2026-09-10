# Phase B current-render manifest

Captured from the Phase B working tree on 2026-09-11 with Playwright 1.55.0 and Chrome. Desktop used 1440 x 1200; mobile used 390 x 844 with a mobile Safari user agent. The rebuilt site was served only on `127.0.0.1:8765`, and the server was stopped after capture.

Desktop article files remain full-page captures. Mobile uses one clean top viewport per Phase B article, one viewport per decoded image card, and before/after viewports for each overflowing table. Four additional viewport artifacts cover an unaffected responsive flowchart and iframe visual at desktop and mobile. `visual-qa.spec.js` contains the assertions; they prove rendered geometry, not editorial approval.

## Image geometry assertions

The affected static images were decoded before capture. Their rendered ratio matches their intrinsic ratio within `0.01`, their full bounding box fits the `.visual-container`, and container height differs from rendered image height by less than one pixel.

| Image / viewport | Natural size | Rendered size | Natural ratio | Rendered ratio | Fits |
| --- | ---: | ---: | ---: | ---: | --- |
| Microsoft / desktop | 1280 x 720 | 670 x 376.875 | 1.77778 | 1.77778 | true |
| Microsoft / mobile | 1280 x 720 | 340 x 191.25 | 1.77778 | 1.77778 | true |
| GitLab / desktop | 1280 x 720 | 670 x 376.875 | 1.77778 | 1.77778 | true |
| GitLab / mobile | 1280 x 720 | 340 x 191.25 | 1.77778 | 1.77778 | true |
| AWS / desktop | 1280 x 1000 | 670 x 523.4375 | 1.28 | 1.28 | true |
| AWS / mobile | 1280 x 1000 | 340 x 265.625 | 1.28 | 1.28 | true |

The unaffected flowchart remained responsive: desktop rendered 672 x 472.594 from a 672 x 472 source; mobile rendered 342 x 801.297 from the 342 x 804 mobile source. Ratio differences were `0.00179` and `0.00143`, and both images fit their `<picture>`. The iframe visual still filled its existing container exactly: 670 x 400 desktop and 340 x 500 mobile.

All four desktop Phase B pages reported `clientWidth=1440`, `scrollWidth=1440`. All four mobile pages reported `clientWidth=390`, `scrollWidth=390`, with `windowY=0` and `documentTop=0` before capture.

## Mobile table assertions

Each overflowing table was reset to `scrollLeft=0`, captured, moved to its maximum scroll position, asserted to have moved, and captured again.

| Article/table | clientWidth | scrollWidth | scrollLeft before -> after |
| --- | ---: | ---: | ---: |
| Onboarding: Dependency / source / check / recovery | 342 | 517 | 0 -> 175 |
| Onboarding: Stage / owner / trigger | 342 | 349 | 0 -> 7 |
| Onboarding: Stage / instruction / evidence | 342 | 415 | 0 -> 73 |
| Review: Claim ledger | 342 | 465 | 0 -> 123 |
| Style guide: Product state / decision / evidence / failure | 342 | 420 | 0 -> 78 |
| Style guide: Page job / shape / completion | 342 | 374 | 0 -> 32 |
| Style guide: UI claim / source / trigger | 342 | 345 | 0 -> 3 |
| Organization: Reader route | 342 | 374 | 0 -> 32 |
| Organization: URL migration | 342 | 682 | 0 -> 340 |

Seven additional tables fit their 342px wrappers and correctly reported `overflow=false`, `before=0`, `after=0`, and `moved=false`.

## Artifact inventory

| Artifact | Pixels | SHA-256 |
| --- | --- | --- |
| `onboarding-desktop.png` | 1440 x 13317 | `b41869410bea4f9921aa711f558f77d488228fcd4f176b7a6541ef0ea468a358` |
| `onboarding-mobile-image-1.png` | 390 x 844 | `a908809034a04e16c0a199f5ab81182aad354e6adf5ac927615d1dbe08a857ad` |
| `onboarding-mobile-image-2.png` | 390 x 844 | `6473bace9c9dcddf9f2a0ce62453d651f9a7bee41fbbc3dd98b39dc7614cfe94` |
| `onboarding-mobile-table-1-after.png` | 390 x 844 | `101090b298fc2b953400f3c32d7676a0ce92ab25a9a602f0eee6e1cbbc64ab70` |
| `onboarding-mobile-table-1-before.png` | 390 x 844 | `387c037a26c723bd91d709f0e99444867bbecbb0b9fd5510d0bbcb1c41a3b930` |
| `onboarding-mobile-table-2-after.png` | 390 x 844 | `abd9827cd51303e0103b50f56b975f4444ae9647f1bdfd107ee127369db4056b` |
| `onboarding-mobile-table-2-before.png` | 390 x 844 | `0fe37c9b8976c8814ad82d992123392375a62084db43aa9a5dc3a99b57bd03ea` |
| `onboarding-mobile-table-3-after.png` | 390 x 844 | `71a8195fd66bccc32b0d56eb3c9a250d6a4b32c575b8490cbb384ec1d606fa58` |
| `onboarding-mobile-table-3-before.png` | 390 x 844 | `b07c492b7589ef41e970d802282a321ee3df0b994e7e27409bfb56c71bda48c1` |
| `onboarding-mobile-top.png` | 390 x 844 | `31cdf0c657e6b49a9b33edf4dca9e56bd1c20219d88ff2adaba2711fe1f0b1af` |
| `organization-desktop.png` | 1440 x 15794 | `91542655b98882620bbb7a3efa641e2163f9f2a0ff01d228614484b7ca388321` |
| `organization-mobile-image-1.png` | 390 x 844 | `c07599248509f157a1b21bdcaef137bd4b9cc8e2e0ebf2ea669ccb77aa95f08e` |
| `organization-mobile-table-2-after.png` | 390 x 844 | `645e7eecf9d72f24fec9ce93e511b4dc87fabb941e701c0beca3ccf7b481dfc0` |
| `organization-mobile-table-2-before.png` | 390 x 844 | `715c2891559f322ad4199921359c1ab89467a7bc58d5bc6262955cc48cc9e78e` |
| `organization-mobile-table-4-after.png` | 390 x 844 | `e27dd62b02e776a0609d30e58960b1dbd9da0cee1b196409f2b06f1b61bf803e` |
| `organization-mobile-table-4-before.png` | 390 x 844 | `ec0ac693589ade117dee5d00e1bf0bf0af9ee6fba687775945546bbf6ceb1bd4` |
| `organization-mobile-top.png` | 390 x 844 | `8a667492e3dcb63cd6d982af1c716bc330bd8a391d4c81484c54985a2bfbcba9` |
| `review-desktop.png` | 1440 x 16100 | `d432e3c3eda216ae3f2b1d62f10e456dfbade0fd0dad053d6b06c96bfcb71eb8` |
| `review-mobile-table-1-after.png` | 390 x 844 | `46589a5bc703229c44c6b53c91bda8124595b53c824deb0cfea5994790c52e16` |
| `review-mobile-table-1-before.png` | 390 x 844 | `aae9d494581652b5e06b83cf7be36f835895b5a247f2f6cb9c70ea0c086f8c52` |
| `review-mobile-top.png` | 390 x 844 | `c6eb1880f31fed74b90f534ea2818504921f45bd6013b54f38b87b5474453682` |
| `style-guide-desktop.png` | 1440 x 9749 | `23f3048e6863f3b36e14610b2450048a8ef1b10135b1ba413f51483c5770abeb` |
| `style-guide-mobile-table-1-after.png` | 390 x 844 | `d5180f289eb06db1a8ea35a77f91ecde8b1c362b8518ab6fabb7952b790fe36f` |
| `style-guide-mobile-table-1-before.png` | 390 x 844 | `76d3548b9216689a2d5134c021229e41be236e3030ad99ed2a0721ca5284a57a` |
| `style-guide-mobile-table-2-after.png` | 390 x 844 | `de4ad1beee8f126f77b6bd95cfebe7003c2c44923f463a1a31613761a40434a9` |
| `style-guide-mobile-table-2-before.png` | 390 x 844 | `0b0f9c285d98b95a175d10c6b200451cce5247d6385af49476421256a952f5df` |
| `style-guide-mobile-table-4-after.png` | 390 x 844 | `e12d72ed9a8cc879d4e51e4d39dc6edafc76539fd2eb6db5ed6e69dc7df3186e` |
| `style-guide-mobile-table-4-before.png` | 390 x 844 | `f50a56d4bde50d253984963a6a74e7c5dc71c558d3a00748fe0d4df01f311ac4` |
| `style-guide-mobile-top.png` | 390 x 844 | `af5b0718efc53d23616e27490d6c1c1c8a5e78cb6522b9bc1d924f6ce6106695` |
| `unaffected-flowchart-desktop.png` | 1440 x 1200 | `88b756f72b90c9fef71492a99c62a48482b0210a9c16fd85496adecfe9e05afc` |
| `unaffected-flowchart-mobile.png` | 390 x 844 | `9e62e581b455f8cd61ed1ea1e856a8aa0bf41fcd2e3ae56c703da9cf7212bc0e` |
| `unaffected-iframe-desktop.png` | 1440 x 1200 | `f84d733a3cd933fcfb9a3c8b5cb4fd618994e7593e4604da559d6f6e3956deb7` |
| `unaffected-iframe-mobile.png` | 390 x 844 | `77ef48f123066b94131506147ad6e63d7be6fb385ed70b5f4207685a5664243e` |

All 33 PNGs were inspected after capture. The three corrected image cards preserve their source proportions and remain fully visible. The representative flowchart and iframe retain their previous rendering behavior. This is implementation-side inspection, not independent visual approval.
