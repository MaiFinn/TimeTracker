from datetime import date
import streamlit as st

from timetracker.config.paths import CONTRACT_FILE, WORK_ENTRIES_FILE
from timetracker.storage.json_storage import load_json
from timetracker.ui.contract_view import render_contract_page
from timetracker.ui.dashboard_view import render_dashboard
from timetracker.ui.work_entry_view import render_work_entry_page


MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

st.title("TimeTracker")

today = date.today()

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_entry_id" not in st.session_state:
    st.session_state.selected_entry_id = None

if "active_year" not in st.session_state:
    st.session_state.active_year = today.year

if "active_month" not in st.session_state:
    st.session_state.active_month = today.month


contract = load_json(CONTRACT_FILE, default=None)
work_entries = load_json(WORK_ENTRIES_FILE, default=[])


if st.session_state.page == "home":
    button_label = "+ Create new contract" if contract is None else "Adapt contract"

    if st.button(button_label):
        st.session_state.page = "contract"
        st.rerun()

    st.divider()

    render_dashboard(
        contract=contract,
        work_entries=work_entries,
        month_names=MONTH_NAMES,
    )

    st.divider()

    render_work_entry_page(
        selected_year=int(st.session_state.active_year),
        selected_month=int(st.session_state.active_month),
    )


elif st.session_state.page == "contract":
    render_contract_page(contract)