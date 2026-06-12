from datetime import date

import pandas as pd
import streamlit as st

from timetracker.reports.monthly_report import (
    build_monthly_report_rows,
    build_total_report_row,
)
from timetracker.storage.json_storage import load_json
from timetracker.ui.contract_view import render_contract_page
from timetracker.ui.dashboard_view import render_dashboard
from timetracker.ui.work_entry_view import render_work_entry_page

from timetracker.config.paths import DATABASE_FILE
from timetracker.storage.sqlite_storage import load_contract, load_work_entries

from timetracker.ui.auth_view import render_login_page, render_logout_button


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

if "user_id" not in st.session_state:
    render_login_page()
    st.stop()

CURRENT_USER_ID = st.session_state.username

render_logout_button()

today = date.today()

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = None

if "selected_entry_id" not in st.session_state:
    st.session_state.selected_entry_id = None

if "view_entry_id" not in st.session_state:
    st.session_state.view_entry_id = None

if "active_year" not in st.session_state:
    st.session_state.active_year = today.year

if "active_month" not in st.session_state:
    st.session_state.active_month = today.month


contract = load_contract(DATABASE_FILE, CURRENT_USER_ID)
work_entries = load_work_entries(DATABASE_FILE, CURRENT_USER_ID)


if st.session_state.page == "home":
    button_label = "+ Create new contract" if contract is None else "Adapt contract"

    col1, spacer, col2 = st.columns([2, 3, 2])

    with col1:
        if st.button(button_label):
            st.session_state.page = "contract"
            st.rerun()

    with col2:
        if contract is not None:
            rows = build_monthly_report_rows(contract, work_entries)
            rows.append(build_total_report_row(contract, work_entries))

            report_data = pd.DataFrame(rows)
            csv_data = report_data.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download report",
                data=csv_data,
                file_name="timetracker_report.csv",
                mime="text/csv",
            )

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