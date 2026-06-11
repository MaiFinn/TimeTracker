from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar

from timetracker.config.paths import ATTACHMENTS_DIR, WORK_ENTRIES_FILE
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
        title_suffix = ""

        if entry.get("note"):
            title_suffix += " 📝"

        if entry.get("attachments"):
            title_suffix += " 📎"

        events.append(
            {
                "id": str(index),
                "title": f"{entry['total_time']}{title_suffix}",
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

    if st.session_state.view_entry_id is not None:
        entry_id = st.session_state.view_entry_id

        if 0 <= entry_id < len(work_entries):
            _render_work_entry_detail(work_entries, entry_id)

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
            st.session_state.view_entry_id = None

    if calendar_result.get("eventClick"):
        if st.session_state.get("selected_entry_id") is not None:
            return

        if st.session_state.get("ignore_next_calendar_click", False):
            st.session_state.ignore_next_calendar_click = False
        else:
            st.session_state.view_entry_id = int(
                calendar_result["eventClick"]["event"]["id"]
            )
            st.session_state.selected_entry_id = None
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
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(
            [2, 2, 2, 2, 3, 1, 1, 2, 2]
        )

        col1.write(entry["date"])
        col2.write(entry["start_time"])
        col3.write(entry["end_time"])
        col4.write(entry["total_time"])
        col5.markdown(
            _render_status_badge(entry.get("entry_status", "worked")),
            unsafe_allow_html=True,
        )
        col6.write("📝" if entry.get("note") else "")
        col7.write("📎" if entry.get("attachments") else "")

        if col8.button(
            "View",
            key=f"view_entry_list_{index}",
            width="stretch",
        ):
            st.session_state.view_entry_id = index
            st.session_state.selected_entry_id = None
            st.session_state.selected_date = None
            st.rerun()

        if col9.button(
            "Edit",
            key=f"edit_entry_list_{index}",
            width="stretch",
        ):
            st.session_state.selected_entry_id = index
            st.session_state.view_entry_id = None
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
    st.session_state.view_entry_id = None


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


def _save_uploaded_files(uploaded_files: list) -> list[dict]:
    """Save uploaded files and return attachment metadata."""

    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)

    attachments = []

    for uploaded_file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = ATTACHMENTS_DIR / f"{timestamp}_{uploaded_file.name}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        attachments.append(
            {
                "file_name": uploaded_file.name,
                "file_path": str(file_path),
            }
        )

    return attachments


def _render_existing_attachments(attachments: list[dict]) -> None:
    """Render existing attachments."""

    if not attachments:
        return

    st.markdown("**Existing attachments**")

    for attachment in attachments:
        st.write(f"📎 {attachment['file_name']}")


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

    note = st.text_area(
        "Note",
        key="new_note",
    )

    uploaded_files = st.file_uploader(
        "Attachments",
        accept_multiple_files=True,
        key="new_attachments",
    )

    if st.button("Save work entry"):
        try:
            attachments = _save_uploaded_files(uploaded_files)

            create_work_entry(
                selected_date,
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M"),
                entry_status=entry_status,
                note=note,
                attachments=attachments,
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

    edit_note = st.text_area(
        "Note",
        value=selected_entry.get("note", ""),
        key="edit_note",
    )

    existing_attachments = selected_entry.get("attachments", [])

    attachments_to_keep = _render_editable_attachments(
        existing_attachments,
        entry_id,
    )

    new_uploaded_files = st.file_uploader(
        "Add more attachments",
        accept_multiple_files=True,
        key="edit_attachments",
    )

    if st.button("Save changes"):
        try:
            new_attachments = _save_uploaded_files(new_uploaded_files)

            work_entries[entry_id] = {
                "date": str(selected_date),
                "start_time": str(edit_start_time),
                "end_time": str(edit_end_time),
                "total_time": calculate_total_time(edit_start_time, edit_end_time),
                "entry_status": edit_entry_status,
                "note": edit_note,
                "attachments": attachments_to_keep + new_attachments,
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

def _render_editable_attachments(
    attachments: list[dict],
    entry_id: int,
) -> list[dict]:
    """Render existing attachments with delete option."""

    if not attachments:
        return []

    st.markdown("**Existing attachments**")

    attachments_to_keep = []

    for index, attachment in enumerate(attachments):
        col1, col2 = st.columns([4, 1])

        col1.write(f"📎 {attachment['file_name']}")

        delete_attachment = col2.checkbox(
            "Delete",
            key=f"delete_attachment_{entry_id}_{index}",
        )

        if not delete_attachment:
            attachments_to_keep.append(attachment)

    return attachments_to_keep

def _render_work_entry_detail(work_entries: list[dict], entry_id: int) -> None:
    """Render detailed work entry view."""

    entry = work_entries[entry_id]

    st.subheader("Work entry details")

    col1, col2, col3 = st.columns(3)
    col1.metric("Date", entry["date"])
    col2.metric("Start", entry["start_time"])
    col3.metric("End", entry["end_time"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Duration", entry["total_time"])
    col2.markdown(
        _render_status_badge(entry.get("entry_status", "worked")),
        unsafe_allow_html=True,
    )

    note = entry.get("note", "")

    if note:
        st.markdown("**Note**")
        st.write(note)

    attachments = entry.get("attachments", [])

    if attachments:
        st.markdown("**Attachments**")

        for attachment in attachments:
            file_path = attachment["file_path"]

            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"📎 {attachment['file_name']}",
                    data=f,
                    file_name=attachment["file_name"],
                    key=f"detail_attachment_{entry_id}_{attachment['file_name']}",
                )

    col1, col2 = st.columns(2)

    if col1.button("Edit entry", width="stretch"):
        st.session_state.selected_entry_id = entry_id
        st.session_state.view_entry_id = None
        st.session_state.selected_date = None
        st.session_state.ignore_next_calendar_click = True
        st.rerun()

    if col2.button("Close", width="stretch"):
        _clear_work_entry_selection()
        st.session_state.ignore_next_calendar_click = True
        st.rerun()