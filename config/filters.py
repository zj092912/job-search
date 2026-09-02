# -*- coding: utf-8 -*-
"""Shared eligibility filters for the job-search backlog.
Mirrors config/candidate_profile.md -> 岗位资格过滤 so the page and the agents agree.

Design bias: a wrongly-dropped junior role is far more costly than a wrongly-kept
senior one. Jun skips a bad row in two seconds; he never sees a dropped one.
So every rule here fires only on positive evidence, and abstains when unsure.
"""
import re, datetime

TODAY = datetime.date(2026, 9, 2)
SALARY_FLOOR_CAP = 130000  # a floor above this *may* signal a senior req

# Employers Jun has confirmed do not sponsor. Grow this by hand only.
NO_SPONSOR = {
    "columbia threadneedle investments": "Jun 确认：坚决不提供 sponsorship",
}
# US public-sector employers: government / state / municipal roles require
# citizenship or permanent residency and do not file H-1B.
PUBLIC_SECTOR = re.compile(
    r'department of|state of |county of |city of |municipal|public schools|'
    r'corrections|federal reserve|port authority', re.I)

# --- entry-level evidence: any one of these disarms the salary proxy ---

# 1) the title states the level
ENTRY_TITLE = re.compile(
    r'\bjunior\b|\bjr\.?\b|\bgraduate\b|\bnew ?grad\b|\bentry[- ]level\b|\bintern\b|'
    r'\btrainee\b|\bcampus\b|\banalyst\s*(i|1)\b|\bassociate\s*(i|1)\b|\blevel\s*(i|1)\b|'
    r'\bearly career\b|\bdesk analyst\b|\b20(26|27)\b', re.I)

# 2) the scan already judged it non-senior (match_reason is written by the filter agent)
ENTRY_REASON = re.compile(
    r'no seniority|entry[- ]level|no explicit years|no years of experience|'
    r'early[- ]career|internship|campus|new ?grad|junior|graduate|'
    r'no senior/lead|analyst i\b', re.I)

# 3) firms whose new-grad comp is simply above the cap — salary says nothing about
#    level here. Quant trading / prop / multistrat shops and the big banks' quant desks.
HIGH_PAY_ENTRY = re.compile(
    r'flow traders|akuna|jane street|hudson river|citadel|imc|optiver|drw|jump trading|'
    r'susquehanna|\bsig\b|five rings|old mission|belvedere|tower research|xtx|radix|'
    r'headlands|jump crypto|two sigma|d\.? ?e\.? shaw|squarepoint|balyasny|millennium|'
    r'point72|man group|aqr|qube|voleon|walleye|schonfeld|verition|ExodusPoint|'
    r'goldman|morgan stanley|\bubs\b|jpmorgan|barclays|citi|deutsche bank|nomura|'
    r'bank of america|wells fargo|hsbc|bnp paribas|societe generale', re.I)


def posted_date(j, first_seen):
    p = (j.get('posted_date') or '').strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', p)
    if m:
        return datetime.date(*map(int, m.groups()))
    for fmt in ('%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.datetime.strptime(p, fmt).date()
        except ValueError:
            pass
    m = re.match(r'^(\d+)\s*days? ago', p)
    if m and first_seen:
        seen = datetime.date(*map(int, first_seen.split('-')))
        return seen - datetime.timedelta(days=int(m.group(1)))
    return None


def age_days(j, first_seen):
    """Age of the posting in days. Shown to Jun, never used to drop anything —
    whether a listing is still open can only be settled by opening it."""
    d = posted_date(j, first_seen)
    return None if d is None else (TODAY - d).days


def salary_floor(j):
    """Lowest number in the salary string, annualized. None if unparseable."""
    s = (j.get('salary') or '').strip()
    if not s or s.upper() in ('N/A', 'NA', '-'):
        return None
    nums = [float(x.replace(',', '')) for x in re.findall(r'\d[\d,]*(?:\.\d+)?', s)]
    if not nums:
        return None
    lo = min(nums)
    hourly = bool(re.search(r'hour|/hr|hr\b', s, re.I))
    if hourly or lo < 500:          # a "floor" under 500 can only be an hourly rate
        lo *= 2080
    return lo


def entry_evidence(j):
    """Why this job is treated as open to a new grad despite the pay. None = no evidence."""
    if ENTRY_TITLE.search(j.get('title') or ''):
        return "标题写明级别"
    if ENTRY_REASON.search(j.get('match_reason') or ''):
        return "抓取时已判定无 seniority 要求"
    if HIGH_PAY_ENTRY.search(j.get('company') or ''):
        return "该公司新人起薪本就高于上限"
    return None


def no_sponsor_reason(j):
    c = (j.get('company') or '').lower()
    for k, why in NO_SPONSOR.items():
        if k in c:
            return why
    if PUBLIC_SECTOR.search(j.get('company') or ''):
        return "美国公营单位 — 通常要求公民/绿卡，不办 H-1B"
    return None


def screen(j, first_seen=None):
    """Return (kept: bool, reason: str|None). reason is why it was dropped.

    No staleness rule: posting age is reported, not filtered on.
    """
    why = no_sponsor_reason(j)
    if why:
        return False, "no-sponsor:" + why

    s = (j.get('salary') or '')
    if re.search(r'hour|/hr|hr\b', s, re.I):
        return True, None      # 时薪是合同工报价，×2080 折算不能当资历信号

    fl = salary_floor(j)
    if fl is not None and fl > SALARY_FLOOR_CAP and not entry_evidence(j):
        return False, "senior:薪资下限 $%s 起，且无任何 entry-level 迹象" % format(int(fl), ',')

    return True, None
