# Candidate Profile — used by scan & filter agents

## ⛔ Deduplication — MANDATORY, do this before anything else

`jobs/seen.json` is the ledger of every job that has already been reported to Jun.
**The filter agent must read it, use it, and update it on every single run.**

**Fingerprint** — the identity of a job is:

```
normalize(company) + "|" + normalize(title) + "|" + normalize(location)
normalize(s) = s.lower(), then replace every run of non-alphanumeric chars with a
               single space, then strip
```

**NEVER key dedupe on `url`.** Indeed mints a brand-new `to.indeed.com/<random>`
short link on every scan, so the same posting looks new forever. That single
mistake put the *same* Intex Solutions "Quantitative Analyst - ABS Modeling"
posting (posted May 26, 2026) into six separate reports — 07-20, 07-27, 07-29,
08-12, 08-19, 08-26 — and made **46% of every report Jun has ever received a
repeat.**

**Filter-stage procedure:**

1. Load `jobs/seen.json`.
2. Dedupe *within* this run first — the same posting often appears several times
   in one raw scan.
3. Drop every job whose fingerprint is already in the ledger, **whatever its
   `status`**. `applied` and `ignored` must never be shown again.
4. Write only the survivors to `jobs/filtered/<date>.json`.
5. Append the survivors to the ledger (`first_seen` = `last_seen` = today,
   `times_seen` = 1, `status` = `"seen"`), and for anything you dropped, bump its
   `times_seen` and `last_seen`. Commit `jobs/seen.json` alongside the filtered file.

**Report-stage:** state both numbers, e.g. `Total new matches: 37 (18 duplicates
suppressed)`. If a run yields 0 new jobs, that is a valid, useful report — say so
rather than widening the filter to fill space.

**Status values:** `seen` = already reported · `applied` = Jun applied, never show
again · `ignored` = Jun looked and passed, never show again. Jun (or Claude) edits
these by hand; agents only ever add rows and bump counters.

## Basics
- Name: Jun Zhang
- Status: International student (F-1 visa). **US roles must offer visa sponsorship** (CPT/OPT/H-1B path). Exclude any US listing that states "no sponsorship" / "must be authorized to work without sponsorship now or in the future".
- Location base: Boston, MA
- Experience level: ~2 months of internship experience total. Target **internship, entry-level, new-grad, associate/analyst I** roles. Exclude roles requiring 2+ years professional experience.

## Education
- M.S. Mathematical Finance & Financial Technology, Boston University Questrom School of Business — expected Jan 2027
  - Coursework: Statistics (R), Programming (Python), Stochastic Calculus, Machine Learning, Computational Math, Financial Econometrics, Fixed Income
- B.Sc. Financial Mathematics, Beijing Institute of Technology, Zhuhai — Jun 2025 (Dean's Scholarship)

## Skills
Python, R, C++, EViews, SQL basics, stochastic calculus, statistical modeling, ML (LightGBM), NLP/RAG, econometrics/regression analysis, fixed income basics

## Relevant experience
- Corporate Relationship Intern, China Minsheng Bank (Tianjin) — credit review, risk data collection for a RMB 100M syndicated loan, client financial statement management
- Algo trading strategy projects (pairs trading, VIX spread) — BU High Frequency Trading
- MLB player valuation regression model (Python)
- Bitcoin forecasting with LightGBM + NLP/RAG on news sentiment
- NCAA basketball win-factor econometric analysis (EViews)
- Languages: Mandarin (native), English (fluent), Cantonese (fluent)

## Target job titles / keywords
- Quant Risk Analyst / Quantitative Risk
- Financial Risk Analyst / Risk Analyst
- Financial Mathematics roles (quant analyst, pricing analyst)
- Data Analyst (finance / banking preferred)
- Also acceptable: Junior Quant Researcher, Credit Risk Analyst, Market Risk Analyst — entry-level

**Focus is QUANTITATIVE risk** — roles centered on modeling, statistics, pricing, data analysis. The word "risk" alone is NOT enough; the role must be quantitative/analytical, not policy/compliance/investigation work. See hard excludes below.

## Target locations (must match one of these; remote counts toward the matching country)
- **United States**: Boston MA, New York NY, New Jersey, California — remote or onsite both OK
- **United Kingdom**: London only
- **China**: Shanghai, Shenzhen, Guangzhou, Hong Kong

## Hard excludes
- US roles explicitly stating no visa sponsorship
- Roles requiring 3+ years of professional experience or a CFA/FRM already in hand as a hard requirement
- Senior/lead/manager-level titles
- **Non-quantitative "regulatory / compliance" roles** — regulatory risk, regulatory affairs, regulatory reporting, compliance analyst, AML/KYC, gaming/casino regulatory, sanctions, audit, internal controls, policy/investigation analyst. These are compliance/research/investigation work, not quantitative modeling, and do not match a quant-risk skillset. Example to exclude: "Analyst - Regulatory Risk" at Hard Rock International (Atlantic City) — a gaming-compliance role.
  - *Do not* exclude a genuine quant/market/credit/model risk role just because it mentions "regulatory capital", "Basel", "CCAR/stress testing", or "regulatory models" — those are quantitative and remain in scope. The exclude applies when the job's core is compliance/policy/investigation rather than modeling or data analysis.
