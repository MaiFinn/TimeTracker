# TimeTracker

A minimal CLI tool to track:

- contract start date
- salary per hour
- planned hours per week/month
- worked hours in a calendar with notes

## Usage

```bash
python time_tracker.py --file tracker.json init \
  --start-date 2026-01-01 \
  --salary-per-hour 35 \
  --hours-per-week 40 \
  --hours-per-month 160
```

```bash
python time_tracker.py --file tracker.json add --date 2026-05-20 --hours 8 --note "Backend work"
python time_tracker.py --file tracker.json calendar --month 2026-05
python time_tracker.py --file tracker.json summary --month 2026-05
```
