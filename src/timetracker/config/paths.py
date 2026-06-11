from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
CONTRACT_FILE = ARTIFACTS_DIR / "contract.json"
WORK_ENTRIES_FILE = ARTIFACTS_DIR / "work_entries.json"
LOG_FILE = ARTIFACTS_DIR / "logs" / "timetracker.log"
ATTACHMENTS_DIR = ARTIFACTS_DIR / "attachments"