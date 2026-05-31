from pathlib import Path

import streamlit as st

from timetracker.storage.json_storage import load_json
from timetracker.ui.contract_view import render_contract_page
from timetracker.ui.work_entry_view import render_work_entry_page

CONTRACT_FILE = Path("artifacts/contract.json")

st.title("TimeTracker")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_entry_id" not in st.session_state:
    st.session_state.selected_entry_id = None


contract = load_json(CONTRACT_FILE, default=None)


if st.session_state.page == "home":
    button_label = "+ Create new contract" if contract is None else "Adapt contract"

    if st.button(button_label):
        st.session_state.page = "contract"
        st.rerun()

    st.divider()

    render_work_entry_page()


elif st.session_state.page == "contract":
    render_contract_page(contract)