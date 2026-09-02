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

## 岗位资格过滤 — 去重之后、写 filtered 之前跑一遍

**总原则:误删一个 junior 岗的代价,远高于误留一个资深岗。**
Jun 扫一眼就能跳过一条不合适的,但被删掉的他永远看不见。
所以下面每条规则都只在**有正面证据**时才生效,拿不准就留着。

**1 — 已投过的公司** 查 `jobs/seen.json` 里 `status` 为 `applied` / `ignored` 的行,
以及公司名匹配的其他岗位。同名公司不同岗位**不要直接丢**,标出来让 Jun 自己判断。

**2 — 过期:不过滤。** ~~按发布日期推算是否下架~~ —— 已于 2026-09-02 按 Jun 的要求废除。
帖子还开不开**只有点进去才知道**,按日期猜会误删还在招的岗位,Jun 宁可自己一个个点。
> 仍然要**算出并展示**发布天数(`posted_date` 三种格式都要能解析:
> `YYYY-MM-DD`、`Month DD, YYYY`、`N days ago`(相对当次抓取日)),
> 让 Jun 自己判断,但**绝不因此丢弃任何岗位**。

**3 — 资深岗(2 年以上经验)** 抓到的数据只有一句话描述,**没有完整 JD,判断不了年限要求**。
按 Jun 的指示改用薪资代理:薪资下限高于 **$130,000** 的丢掉 —— **但只在毫无 entry-level 迹象时**。
- 薪资下限 = 薪资字符串里最小的那个数;小于 500 的数字视为时薪。
- **时薪岗位一律不受这条限制** —— 合同工报价 ×2080 折算出来的数字不能当资历信号。
- **下列任一成立即豁免,保留:**
  1. **标题写明级别**:`junior` / `jr` / `graduate` / `new grad` / `entry-level` / `intern` /
     `trainee` / `campus` / `early career` / `analyst I` / `associate I` / `desk analyst` /
     `2026` / `2027`
  2. **抓取时已判定无 seniority 要求** —— `match_reason` 里出现
     "no seniority markers" / "no seniority indicated" / "entry-level ..." /
     "no explicit years" 等。这是 filter agent 自己写的判断,比薪资可信。
  3. **该公司新人起薪本就高于上限** —— 自营/对冲/投行 quant 岗:Flow Traders、Akuna、
     Jane Street、HRT、Citadel、IMC、Optiver、DRW、Jump、SIG、Five Rings、XTX、
     Two Sigma、D.E. Shaw、Balyasny、Millennium、Point72、AQR、Walleye、Schonfeld,
     以及 Goldman / Morgan Stanley / UBS / JPMorgan / Citi / BofA 等的 quant 岗。
- 没写薪资的**保留**,无法判断不等于不合格。
> **为什么要这么松:** 只按 $130k 硬切会误杀 Flow Traders 的 Junior Quantitative Researcher
> ($175k)、Akuna 的 Junior QR($145k)、UBS 的 Quantitative Analyst($145k,抓取时标注
> "no seniority indicated")、Balyasny 的 Quantitative Researcher($150k)——
> 这些恰恰是 Jun 最该投的岗位。加上豁免后,被这条挡下的从 11 个降到 6 个。

**4 — 不提供 sponsorship** Jun 是 F-1,美国岗必须能 sponsor。同样**无法逐个核实**,
目前两类丢掉:
- **确认名单**(Jun 亲自确认过的,只能手动加):
  - `Columbia Threadneedle Investments` — 坚决不提供 sponsorship
- **美国公营单位** — 公司名匹配 `department of` / `state of` / `county of` / `city of` /
  `municipal` / `public schools` / `corrections` / `federal reserve` / `port authority`。
  政府/州/市级岗位要求公民或绿卡,不办 H-1B。
> ⚠️ 抓取数据里的 "no no-sponsorship language found" **不等于该公司会 sponsor**,
> 那只表示 JD 里没写明拒绝。不要把它当作通过的依据。
> Jun 再确认哪家不 sponsor,就往上面的名单里加一行。

参考实现:`config/filters.py`(台账页面直接跑的就是它)。当前一轮的结果:
468 去重 → 剔除已投 58 / 资深 6 / 不 sponsor 3 → **保留 401**。

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
