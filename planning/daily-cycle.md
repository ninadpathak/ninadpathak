# Daily cycle log

Maintained by `tools/daily_cycle.py`, one authoritative section per date. Deterministic checks only — no judgment,
no interpretation. This exists so the campaign keeps a measurement record even
when no agent session is running. Search Console lags about three days, so each
row's window ends three days before its date.

## 2026-08-17

- Publish: shipped 6aee7e62 content: publish AI crawler and extractability guides
- 28d to 2026-08-14: 11 clicks / 1573 impressions, avg pos 14.6
- Non-brand floor (named queries only, Search Console withholds the long tail): 0 clicks / 247 impressions
- Human-only estimate (non-brand minus machine query fan-out): 0 clicks / 97 impressions. Fan-out removed: 0 clicks / 149 impressions of 314 named
- Human-only is an **estimate, not a bound**: it undercounts because the withheld long tail is excluded entirely, and overcounts because fan-out is only detected within this 28d window, so a family with fewer than three variants here still counts as human
- Distance to 10,000/month: **no non-brand clicks in any named query**
- Publish gate: PASS
- Deploy: LIVE, matches the build
- URL inventory: 1047 URLs tracked since 2025-04-21; refreshed 0d ago; no dead URL still earning; 3 possible soft 404 redirect(s) to review; 3 being dropped by Google; 1 retired-on-purpose still earning; impressions are floors
