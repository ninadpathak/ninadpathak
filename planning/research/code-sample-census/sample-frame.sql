-- Frozen primary sample frame for the code-sample validity census.
-- Source: ClickPy mirror of PyPI Linehaul data.
-- Window: 30 complete dates ending 2026-08-16.
SELECT
    project,
    sum(count) AS downloads
FROM pypi.pypi_downloads_per_day
WHERE date BETWEEN toDate('2026-07-18') AND toDate('2026-08-16')
GROUP BY project
ORDER BY downloads DESC, project ASC
LIMIT 100
FORMAT CSVWithNames

