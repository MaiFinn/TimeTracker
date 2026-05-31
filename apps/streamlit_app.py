from pathlib import Path

import streamlit as st

from timetracker.storage.json_storage import load_json
from timetracker.summary import calculate_work_balance
from timetracker.ui.contract_view import render_contract_page
from timetracker.ui.work_entry_view import render_work_entry_page

CONTRACT_FILE = Path("artifacts/contract.json")
WORK_ENTRIES_FILE = Path("artifacts/work_entries.json")

st.title("TimeTracker")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_entry_id" not in st.session_state:
    st.session_state.selected_entry_id = None


contract = load_json(CONTRACT_FILE, default=None)
work_entries = load_json(WORK_ENTRIES_FILE, default=[])


if st.session_state.page == "home":
    button_label = "+ Create new contract" if contract is None else "Adapt contract"

    if st.button(button_label):
        st.session_state.page = "contract"
        st.rerun()

    st.divider()

    if contract is not None:
        balance = calculate_work_balance(contract, work_entries)

        col1, col2, col3 = st.columns(3)

        col1.metric("Actual hours", f"{balance['actual_hours']:.2f} h")
        col2.metric("Expected hours", f"{balance['expected_hours']:.2f} h")
        col3.metric("Balance", f"{balance['balance_hours']:.2f} h")
    else:
        st.info("Create a contract to see your working time balance.")

    st.divider()

    render_work_entry_page()


elif st.session_state.page == "contract":
    render_contract_page(contract)