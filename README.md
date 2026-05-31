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