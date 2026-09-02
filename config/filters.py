# -*- coding: utf-8 -*-
"""Shared eligibility filters for the job-search backlog.
Mirrors config/candidate_profile.md -> 岗位资格过滤 so the page and the agents agree."""
import re, datetime

TODAY = datetime.date(2026, 9, 2)
MAX_AGE_DAYS = 45          # Indeed listings typically go stale past ~6 weeks
SALARY_FLOOR_CAP = 130000  # a floor above this signals a senior req, not new-grad

# Employers Jun has confirmed do not sponsor. Grow this by hand only.
NO_SPONSOR = {
    "columbia threadneedle investments": "Jun 确认：坚决不提供 sponsorship",
}
# US public-sector employers: government / state / municipal roles require
# citizenship or permanent residency and do not file H-1B.
PUBLIC_SECTOR = re.compile(
    r'department of|state of |county of |city of |municipal|public schools|'
    r'\bdoc\b|corrections|federal reserve|port authority', re.I)


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


# A title that states the level outranks the salary proxy: top prop shops pay
# new grads well over $130k, and dropping those loses exactly the roles Jun wants.
ENTRY_TITLE = re.compile(
    r'\bjunior\b|\bjr\.?\b|\bgraduate\b|\bnew ?grad\b|\bentry[- ]level\b|\bintern\b|'
    r'\btrainee\b|\banalyst i\b|\bassociate i\b|\blevel i\b|\b20(26|27)\b', re.I)


def no_sponsor_reason(j):
    c = (j.get('company') or '').lower()
    for k, why in NO_SPONSOR.items():
        if k in c:
            return why
    if PUBLIC_SECTOR.search(j.get('company') or ''):
        return "美国公营单位 — 通常要求公民/绿卡，不办 H-1B"
    return None


def screen(j, first_seen):
    """Return (kept: bool, reason: str|None). reason is why it was dropped."""
    why = no_sponsor_reason(j)
    if why:
        return False, "no-sponsor:" + why
    a = age_days(j, first_seen)
    if a is not None and a > MAX_AGE_DAYS:
        return False, "stale:发布于 %d 天前" % a
    fl = salary_floor(j)
    if fl is not None and fl > SALARY_FLOOR_CAP and not ENTRY_TITLE.search(j.get('title') or ''):
        return False, "senior:薪资下限 $%s 起，大概率非 junior" % format(int(fl), ',')
    return True, None
