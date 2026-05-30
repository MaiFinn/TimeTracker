import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from streamlit_calendar import calendar

from timetracker.contract_handler import create_contract
from timetracker.work_entry_handler import create_work_entry

CONTRACT_FILE = Path("artifacts/contract.json")
WORK_ENTRIES_FILE = Path("artifacts/work_entries.json")

st.title("TimeTracker")


def load_contract() -> dict | None:
    if CONTRACT_FILE.exists():
        with open(CONTRACT_FILE, "r") as f:
            return json.load(f)
    return None


def load_work_entries() -> list[dict]:
    if WORK_ENTRIES_FILE.exists():
        with open(WORK_ENTRIES_FILE, "r") as f:
            return json.load(f)
    return []


def save_work_entries(work_entries: list[dict]) -> None:
    WORK_ENTRIES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(WORK_ENTRIES_FILE, "w") as f:
        json.dump(work_entries, f, indent=4)


def calculate_total_time(start_time, end_time) -> str:
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    duration = end_datetime - start_datetime
    return str(duration)


def work_entries_to_calendar_events(work_entries: list[dict]) -> list[dict]:
    events = []

    for index, entry in enumerate(work_entries):
        events.append(
            {
                "id": str(index),
                "title": entry["total_time"],
                "start": f"{entry['date']}T{entry['start_time']}",
                "end": f"{entry['date']}T{entry['end_time']}",
            }
        )

    return events


if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_entry_id" not in st.session_state:
    st.session_state.selected_entry_id = None


contract = load_contract()


if st.session_state.page == "home":
    button_label = "+ Create new contract" if contract is None else "Adapt contract"

    if st.button(button_label):
        st.session_state.page = "contract"
        st.rerun()

    st.divider()
    st.subheader("Work calendar")

    work_entries = load_work_entries()
    calendar_events = work_entries_to_calendar_events(work_entries)

    calendar_result = calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "selectable": True,
            "selectMirror": True,
            "editable": False,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
        },
        key="work_calendar",
    )

    if calendar_result.get("dateClick"):
        selected_date = calendar_result["dateClick"]["date"][:10]
        st.session_state.selected_date = selected_date
        st.session_state.selected_entry_id = None

    if calendar_result.get("eventClick"):
        event_id = int(calendar_result["eventClick"]["event"]["id"])
        st.session_state.selected_entry_id = event_id
        st.session_state.selected_date = None

    if st.session_state.selected_date is not None:
        st.subheader(f"Add work entry for {st.session_state.selected_date}")

        start_time = st.time_input("Start time", key="new_start_time")
        end_time = st.time_input("End time", key="new_end_time")

        if st.button("Save work entry"):
            create_work_entry(
                st.session_state.selected_date,
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M"),
            )

            st.success("Work entry saved.")
            st.session_state.selected_date = None
            st.rerun()

    if st.session_state.selected_entry_id is not None:
        entry_id = st.session_state.selected_entry_id

        if 0 <= entry_id < len(work_entries):
            selected_entry = work_entries[entry_id]

            st.subheader("Edit work entry")

            selected_date = st.date_input(
                "Date",
                value=datetime.strptime(selected_entry["date"], "%Y-%m-%d").date(),
                key="edit_date",
            )

            edit_start_time = st.time_input(
                "Start time",
                value=datetime.strptime(selected_entry["start_time"], "%H:%M:%S").time(),
                key="edit_start_time",
            )

            edit_end_time = st.time_input(
                "End time",
                value=datetime.strptime(selected_entry["end_time"], "%H:%M:%S").time(),
                key="edit_end_time",
            )

            if st.button("Save changes"):
                work_entries[entry_id] = {
                    "date": str(selected_date),
                    "start_time": str(edit_start_time),
                    "end_time": str(edit_end_time),
                    "total_time": calculate_total_time(edit_start_time, edit_end_time),
                }

                save_work_entries(work_entries)

                st.success("Work entry updated.")
                st.session_state.selected_entry_id = None
                st.rerun()

            if st.button("Delete work entry"):
                work_entries.pop(entry_id)
                save_work_entries(work_entries)

                st.success("Work entry deleted.")
                st.session_state.selected_entry_id = None
                st.rerun()


elif st.session_state.page == "contract":
    st.subheader("Contract details")

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()

    if contract is not None:
        default_start_date = datetime.strptime(
            contract["start_date"],
            "%Y-%m-%d",
        ).date()
    else:
        default_start_date = None

    company_name = st.text_input(
        "Company name",
        value=contract["company_name"] if contract else "",
    )

    start_date = st.date_input(
        "Start date",
        value=default_start_date,
    )

    salary_per_hour = st.number_input(
        "Salary per hour",
        min_value=0.0,
        value=float(contract["salary_per_hour"]) if contract else 20.0,
    )

    hours_per_week = st.number_input(
        "Hours per week",
        min_value=0.0,
        value=float(contract["hours_per_week"]) if contract else 5.0,
    )

    if st.button("Save contract"):
        create_contract(
            company_name=company_name,
            start_date=str(start_date),
            salary_per_hour=salary_per_hour,
            hours_per_week=hours_per_week,
        )

        st.success("Contract saved.")
        st.session_state.page = "home"
        st.rerun()