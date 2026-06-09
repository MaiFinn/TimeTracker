from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar

from timetracker.config.paths import WORK_ENTRIES_FILE
from timetracker.storage.json_storage import load_json, save_json
from timetracker.utils.time_utils import calculate_total_time
from timetracker.work_entry_handler import create_work_entry

ENTRY_STATUS_OPTIONS = {
    "Worked": "worked",
    "Cancelled by employee": "cancelled_by_employee",
    "Cancelled by employer": "cancelled_by_employer",
}

ENTRY_STATUS_COLORS = {
    "worked": "#2E7D32",
    "cancelled_by_employer": "#1565C0",
    "cancelled_by_employee": "#C62828",
}


def work_entries_to_calendar_events(work_entries: list[dict]) -> list[dict]:
    """Convert work entries to calendar events."""

    events = []

    for index, entry in enumerate(work_entries):
        entry_status = entry.get("entry_status", "worked")

        events.append(
            {
                "id": str(index),
                "title": entry["total_time"],
                "start": f"{entry['date']}T{entry['start_time']}",
                "end": f"{entry['date']}T{entry['end_time']}",
                "backgroundColor": ENTRY_STATUS_COLORS.get(entry_status, "#2E7D32"),
                "borderColor": ENTRY_STATUS_COLORS.get(entry_status, "#2E7D32"),
            }
        )

    return events


def render_work_entry_page(
    selected_year: int,
    selected_month: int,
) -> None:
    """Render the work entry page."""

    view_mode = st.radio(
        "Work entry view",
        options=["Calendar", "List"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.subheader("Work calendar" if view_mode == "Calendar" else "Work entry list")

    work_entries = load_json(WORK_ENTRIES_FILE, default=[])

    if view_mode == "Calendar":
        _render_calendar_view(
            work_entries=work_entries,
            selected_year=selected_year,
            selected_month=selected_month,
        )
    else:
        _render_work_entry_list(work_entries)

    if st.session_state.selected_date is not None:
        _render_add_work_entry_form(st.session_state.selected_date)

    if st.session_state.selected_entry_id is not None:
        entry_id = st.session_state.selected_entry_id

        if 0 <= entry_id < len(work_entries):
            _render_edit_work_entry_form(work_entries, entry_id)


def _render_calendar_view(
    work_entries: list[dict],
    selected_year: int,
    selected_month: int,
) -> None:
    """Render work entries as calendar."""

    calendar_events = work_entries_to_calendar_events(work_entries)
    initial_date = f"{selected_year}-{selected_month:02d}-01"

    col1, col2, col3 = st.columns(3)

    if col1.button("← Previous month"):
        if st.session_state.active_month == 1:
            st.session_state.active_month = 12
            st.session_state.active_year -= 1
        else:
            st.session_state.active_month -= 1

        _clear_work_entry_selection()
        st.rerun()

    if col2.button("Today"):
        today = datetime.today()
        st.session_state.active_year = today.year
        st.session_state.active_month = today.month

        _clear_work_entry_selection()
        st.rerun()

    if col3.button("Next month →"):
        if st.session_state.active_month == 12:
            st.session_state.active_month = 1
            st.session_state.active_year += 1
        else:
            st.session_state.active_month += 1

        _clear_work_entry_selection()
        st.rerun()

    calendar_result = calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "initialDate": initial_date,
            "selectable": True,
            "selectMirror": True,
            "editable": True,
            "displayEventTime": False,
            "headerToolbar": {
                "left": "",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay",
            },
        },
        callbacks=[
            "dateClick",
            "eventClick",
            "datesSet",
        ],
        key=f"work_calendar_{selected_year}_{selected_month}",
    )

    if not calendar_result:
        return

    if calendar_result.get("dateClick"):
        if st.session_state.get("ignore_next_calendar_click", False):
            st.session_state.ignore_next_calendar_click = False
        else:
            clicked_datetime = datetime.fromisoformat(
                calendar_result["dateClick"]["date"].replace("Z", "+00:00")
            )
            selected_date = clicked_datetime.astimezone().date().isoformat()
            st.session_state.selected_date = selected_date
            st.session_state.selected_entry_id = None

    if calendar_result.get("eventClick"):
        if st.session_state.get("ignore_next_calendar_click", False):
            st.session_state.ignore_next_calendar_click = False
        else:
            st.session_state.selected_entry_id = int(
                calendar_result["eventClick"]["event"]["id"]
            )
            st.session_state.selected_date = None

    if calendar_result.get("datesSet") or calendar_result.get("callback") == "datesSet":
        _sync_balance_month_with_calendar(calendar_result)


def _render_work_entry_list(work_entries: list[dict]) -> None:
    """Render work entries as a list."""
    
    if st.button("+ Add work entry", key="add_entry_list"):
        st.session_state.selected_date = datetime.today().date().isoformat()
        st.session_state.selected_entry_id = None
        st.rerun()

    if not work_entries:
        st.info("No work entries yet.")
        return

    for index, entry in enumerate(work_entries):
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 3, 2])

        col1.write(entry["date"])
        col2.write(entry["start_time"])
        col3.write(entry["end_time"])
        col4.write(entry["total_time"])
        col5.markdown(
            _render_status_badge(entry.get("entry_status", "worked")),
            unsafe_allow_html=True,
        )

        if col6.button(
            "Edit",
            key=f"edit_entry_list_{index}",
            use_container_width=True,
        ):
            st.session_state.selected_entry_id = index
            st.session_state.selected_date = None
            st.rerun()


def _render_status_badge(status_value: str) -> str:
    """Render status with colored dot."""

    status_label = _get_status_label(status_value)
    status_color = ENTRY_STATUS_COLORS.get(status_value, "#2E7D32")

    return (
        f"<span style='color:{status_color}; font-size:18px;'>●</span> "
        f"{status_label}"
    )


def _clear_work_entry_selection() -> None:
    """Clear selected work entry state."""

    st.session_state.selected_date = None
    st.session_state.selected_entry_id = None


def _sync_balance_month_with_calendar(calendar_result: dict) -> None:
    """Synchronize selected balance month with the current calendar month."""

    dates_set = calendar_result.get("datesSet", {})
    view = dates_set.get("view", {})

    current_start = (
        view.get("currentStart")
        or dates_set.get("startStr")
        or dates_set.get("start")
    )

    if current_start is None:
        return

    current_date = datetime.fromisoformat(current_start[:10]).date()

    if (
        current_date.year != st.session_state.active_year
        or current_date.month != st.session_state.active_month
    ):
        st.session_state.active_year = current_date.year
        st.session_state.active_month = current_date.month
        _clear_work_entry_selection()
        st.rerun()


def _get_status_label(status_value: str) -> str:
    """Get UI label for an entry status value."""

    for label, value in ENTRY_STATUS_OPTIONS.items():
        if value == status_value:
            return label

    return "Worked"


def _render_add_work_entry_form(selected_date: str) -> None:
    """Render form to add a new work entry."""

    st.subheader(f"Add work entry for {selected_date}")

    start_time = st.time_input("Start time", key="new_start_time")
    end_time = st.time_input("End time", key="new_end_time")

    entry_status_label = st.selectbox(
        "Entry status",
        options=list(ENTRY_STATUS_OPTIONS.keys()),
        index=0,
        key="new_entry_status",
    )

    entry_status = ENTRY_STATUS_OPTIONS[entry_status_label]

    if st.button("Save work entry"):
        try:
            create_work_entry(
                selected_date,
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M"),
                entry_status=entry_status,
            )

            st.success("Work entry saved.")
            _clear_work_entry_selection()
            st.session_state.ignore_next_calendar_click = True
            st.rerun()

        except ValueError as error:
            st.error(str(error))


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

    current_status = selected_entry.get("entry_status", "worked")
    current_status_label = _get_status_label(current_status)

    edit_entry_status_label = st.selectbox(
        "Entry status",
        options=list(ENTRY_STATUS_OPTIONS.keys()),
        index=list(ENTRY_STATUS_OPTIONS.keys()).index(current_status_label),
        key="edit_entry_status",
    )

    edit_entry_status = ENTRY_STATUS_OPTIONS[edit_entry_status_label]

    if st.button("Save changes"):
        try:
            work_entries[entry_id] = {
                "date": str(selected_date),
                "start_time": str(edit_start_time),
                "end_time": str(edit_end_time),
                "total_time": calculate_total_time(edit_start_time, edit_end_time),
                "entry_status": edit_entry_status,
            }

            save_json(WORK_ENTRIES_FILE, work_entries)

            st.success("Work entry updated.")
            _clear_work_entry_selection()
            st.session_state.ignore_next_calendar_click = True
            st.rerun()

        except ValueError as error:
            st.error(str(error))

    if st.button("Delete work entry"):
        work_entries.pop(entry_id)
        save_json(WORK_ENTRIES_FILE, work_entries)

        st.success("Work entry deleted.")
        _clear_work_entry_selection()
        st.session_state.ignore_next_calendar_click = True
        st.rerun()