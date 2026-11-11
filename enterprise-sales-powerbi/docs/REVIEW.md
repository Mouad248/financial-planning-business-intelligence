# Recovery review — 2026-11-09

The archive contains a PBIX, seven SQL scripts, planning inputs and report screenshots. It provides a useful BI learning base. Full Desktop refresh and live SQL/DAX execution are not established by reading those files.

## Changes

- Changed customer, buying-group, salesperson and supplier names to neutral ID labels in SQL views; email/phone fields return null.
- Renamed the target file to the documented CSV filename while preserving its contents.
- Added repeatable planning-data validation and monthly-budget normalization.
- Added executable SQL uniqueness, relationship, identity-mask and financial-total checks.
- Cleared Office document creator/editor/company properties.
- Added a supported refresh/anonymization checklist.

## Evidence

**Verified in source:** fact/dimension SQL, planning files, PBIX ZIP/report layout and screenshots. Layout contains executive and sales-performance pages plus hidden/diagnostic pages.

**Verified by execution:** `reports/supporting_data_validation.json`; any additional checks are in `docs/verification.json`.

**Documented, not yet independently verified:** full live DAX/filter behaviour, visual interactions and database refresh. Cached aggregates and target derivations were reproduced independently of the DAX engine.

**Proposed:** a freshly saved anonymous PBIX, new report screenshots, service deployment/RLS/performance enhancements.

**Unknown:** archive authorship and any real-world organizational use. No clients or business impact are claimed.

## Sharing boundary

The original compressed PBIX and identity-bearing screenshots are under `.private/original-report/` and must remain private until fully refreshed and inspected. Public sample identities still conflict with the requested anonymous presentation. Source SQL pseudonyms preserve join keys; they are not a general privacy guarantee for real microdata. See `powerbi/REFRESH_ANONYMOUS_REPORT.md`.

## Cached-model verification

Read-only PBIX decoding recovered 66 DAX measures and 10 M definitions, now exported without personal source paths. Python reproduced the documented cached fact totals and all 30 prior-year target derivations. This promotes those aggregates and formula presence to executed/source evidence, while SQL Server refresh, DAX engine results and visual filter interactions remain unverified. Individual parameterized `.pq` files and a monthly aggregate CSV are included.
