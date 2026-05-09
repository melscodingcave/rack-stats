# 🤖 AI-NOTES.md — How AI Was Used in This Project

This file documents where and how AI tooling assisted in building `rack-stats`. See [AI-WORKFLOW.md](https://github.com/melscodingcave/the-playbook/blob/main/AI-WORKFLOW.md) in `the-playbook` for the full philosophy.

---

## Log

### Data Model — Domain Knowledge Corrections
**What happened:** AI proposed a Round field on Match and generic location strings for venues.

**What I changed:** 
- Removed Round — adds no analytical value in this context
- Added real Florida venue names with accurate city locations
- Added Payout to Tournament — meaningful financial metric for the billiards community

**Why it matters:** Generic data models produce generic dashboards. Domain knowledge produced a dataset that reflects how Florida billiards tournaments actually operate.

---

### Tournament Types — Handicap vs Open
**What happened:** AI generated a single tournament type with one Fargo range and one entry fee.

**What I changed:** Split into two distinct tournament types with different rules:
- Handicap: Fargo 650 and under, double elimination, $20-50 entry
- Open: Fargo 550-750, single elimination, $100-200 entry
- Only specific venues host open tournaments based on real-world knowledge

**Why it matters:** This distinction is fundamental to how billiards tournaments are organized. Treating all tournaments the same would produce meaningless data.

---

### Player Names — Comic Book Theme
**What happened:** AI generated generic placeholder names.

**What I changed:** Replaced with 16 Marvel and 16 DC comic book characters — making the dataset memorable and personality-driven without using real player names.

**Why it matters:** Portfolio projects benefit from memorable details. A hiring manager who sees "Diana Prince leads the Florida billiards circuit" will remember this project.

---

### Race Lengths — Domain Accuracy
**What happened:** AI generated a single race length for all game types.

**What I changed:** Race to 7 for 9/10-ball, race to 3 or 5 for Banks — reflecting real tournament formats.

**Why it matters:** Banks is a shorter-format game. The avg racks per match visualization confirms this — Banks averaging ~6 racks vs 10 for 9/10-ball. Domain accuracy produces meaningful analytics.

---

### Database Path — Absolute vs Relative
**What happened:** SQLite connection string used a relative path (`data/rack_stats.db`) which broke when running scripts from different directories.

**What I changed:** Updated `get_engine()` to use `os.path.dirname(__file__)` for an absolute path regardless of working directory.

**Why it matters:** Relative paths are a common source of environment-specific bugs. Absolute paths derived from the file location are more robust across different execution contexts.

---

### Documented Intent — Match Count Accuracy
The bracket simulation generates more matches than a real double elimination bracket would produce for a given field size. A production implementation would model the winner's bracket and loser's bracket separately, tracking each player's elimination status. Documented as a known limitation — the pipeline demonstrates ETL, aggregation, and visualization correctly regardless of this constraint.