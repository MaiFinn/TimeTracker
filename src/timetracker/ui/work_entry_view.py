from datetime import datetime
from pathlib import Path

import streamlit as st
from streamlit_calendar import calendar

from timetracker.storage.json_storage import load_json, save_json
from timetracker.work_entry_handler import create_work_entry

WORK_ENTRIES_FILE = Path("artifacts/work_entries.json")


def calculate_total_time(start_time, end_time) -> str:
    """Calculate total working time between start and end time."""

    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)

    duration = end_datetime - start_datetime

    return str(duration)


def work_entries_to_calendar_events(work_entries: list[dict]) -> list[dict]:
    """Convert work entries to calendar events."""

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


def render_work_entry_page() -> None:
    """Render the work entry calendar page."""

    st.subheader("Work calendar")

    work_entries = load_json(WORK_ENTRIES_FILE, default=[])
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
        _render_add_work_entry_form(st.session_state.selected_date)

    if st.session_state.selected_entry_id is not None:
        entry_id = st.session_state.selected_entry_id

        if 0 <= entry_id < len(work_entries):
            _render_edit_work_entry_form(work_entries, entry_id)


def _render_add_work_entry_form(selected_date: str) -> None:
    """Render form to add a new work entry."""

    st.subheader(f"Add work entry for {selected_date}")

    start_time = st.time_input("Start time", key="new_start_time")
    end_time = st.time_input("End time", key="new_end_time")

    if st.button("Save work entry"):
        create_work_entry(
            selected_date,
            start_time.strftime("%H:%M"),
            end_time.strftime("%H:%M"),
        )

        st.success("Work entry saved.")
        st.session_state.selected_date = None
        st.rerun()


def _render_edit_work_entry_form(work_entries: list[dict], entry_id: int) -> None:
    """Render form to edit an existing work entry."""

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

        save_json(WORK_ENTRIES_FILE, work_entries)

        st.success("Work entry updated.")
        st.session_state.selected_entry_id = None
        st.rerun()

    if st.button("Delete work entry"):
        work_entries.pop(entry_id)
        save_json(WORK_ENTRIES_FILE, work_entries)

        st.success("Work entry deleted.")
        st.session_state.selected_entry_id = None
        st.rerun()