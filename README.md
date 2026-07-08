# Job Search Pipeline

Three scheduled cloud agents share this repo as a data bus:

1. **Scanner** — searches Indeed / ZipRecruiter for target roles, writes raw results to `jobs/raw/YYYY-MM-DD.json`
2. **Filter** — reads the latest `jobs/raw/*.json`, scores/filters against `config/candidate_profile.md`, writes `jobs/filtered/YYYY-MM-DD.json`
3. **Weekly report** — reads recent `jobs/filtered/*.json`, writes `reports/YYYY-MM-DD.md` and emails it

See `config/candidate_profile.md` for target roles, locations, and filter rules (edit this file to tune the pipeline — the agents read it fresh each run).

## Layout
```
config/candidate_profile.md   candidate background + filter criteria (source of truth)
jobs/raw/                     raw scan results, one file per scan run
jobs/filtered/                filtered/scored results, one file per filter run
reports/                      generated reports
```
