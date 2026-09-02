# Job Search Pipeline

Three scheduled cloud agents share this repo as a data bus:

1. **Scanner** — searches Indeed / ZipRecruiter for target roles, writes raw results to `jobs/raw/YYYY-MM-DD.json`
2. **Filter** — reads the latest `jobs/raw/*.json`, drops anything already in `jobs/seen.json`, scores/filters the rest against `config/candidate_profile.md`, writes `jobs/filtered/YYYY-MM-DD.json` **and updates `jobs/seen.json`**
3. **Weekly report** — reads recent `jobs/filtered/*.json`, writes `reports/YYYY-MM-DD.md` and emails it

See `config/candidate_profile.md` for target roles, locations, and filter rules (edit this file to tune the pipeline — the agents read it fresh each run).

## Deduplication

`jobs/seen.json` is the ledger of every job already reported. A job's identity is
`company|title|location`, normalized — **never the URL**, because Indeed issues a
fresh `to.indeed.com` short link on every scan. Keying on the URL is what let one
Intex Solutions posting appear in six reports and made 46% of all reported rows
duplicates. The full contract the filter agent must follow is at the top of
`config/candidate_profile.md`.

Mark a row `"status": "applied"` or `"ignored"` in `jobs/seen.json` and it will
never be surfaced again.

## Layout
```
config/candidate_profile.md   candidate background + filter criteria (source of truth)
jobs/raw/                     raw scan results, one file per scan run
jobs/filtered/                filtered/scored results, one file per filter run
jobs/seen.json                dedupe ledger — every job ever reported
reports/                      generated reports
```
