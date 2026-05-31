# TimeTracker

TimeTracker is a lightweight Python application for tracking working hours, contracts and work balances.

The project provides:

- Contract management
- Work entry management
- Interactive calendar-based UI
- Working time summaries and balances
- Dashboard visualizations
- Command line interface
- Automated tests

---

# Features

## Contract Management

Create and modify contracts including:

- Company name
- Contract start date
- Hourly salary
- Expected working hours per week

## Work Entry Tracking

Create and edit work entries with:

- Working date
- Start time
- End time
- Automatically calculated duration

## Dashboard

The dashboard includes:

- Total working time balance
- Monthly balance calculation
- Balance history visualization
- Interactive month synchronization with calendar

## Calendar UI

Interactive calendar with:

- Monthly / weekly / daily views
- Click-to-create work entries
- Edit existing entries
- Calendar synchronization with dashboard

## CLI

Includes commands for:

- Creating contracts
- Creating work entries
- Viewing summaries

---

# Installation

Clone repository:

```bash
git clone <repository-url>

cd TimeTracker
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment:

Mac / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install package:

```bash
pip install -e ".[dev]"
```

---

# Running Streamlit App

```bash
streamlit run apps/streamlit_app.py
```

---

# CLI Usage

Create contract:

```bash
timetracker create-new-contract \
-c "Audi" \
-s "2026-05-01" \
-sph 21 \
-hpw 5
```

Add work entry:

```bash
timetracker add-work-entry \
-wd "2026-05-01" \
-st "08:00" \
-et "12:00"
```

Show summary:

```bash
timetracker summary
```

---

# Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

---

# Project Structure

```text
TimeTracker/

├── apps/
│   └── streamlit_app.py
│
├── artifacts/
│   ├── contract.json
│   ├── work_entries.json
│   └── logs/
│
├── src/
│   └── timetracker/
│       ├── cli.py
│       ├── contract_handler.py
│       ├── work_entry_handler.py
│       ├── summary.py
│       │
│       ├── config/
│       │   └── paths.py
│       │
│       ├── storage/
│       │   └── json_storage.py
│       │
│       ├── ui/
│       │   ├── contract_view.py
│       │   ├── dashboard_view.py
│       │   └── work_entry_view.py
│       │
│       └── utils/
│           ├── logger.py
│           └── time_utils.py
│
└── tests/
```

---

# Development Philosophy

This project emphasizes:

- Simple architecture
- Separation of concerns
- Testability
- Reproducibility
- Small modular components
- Readable code

---

# License

MIT License