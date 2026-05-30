import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from timetracker.contract_handler import create_contract
from timetracker.work_entry_handler import create_work_entry

CONTRACT_FILE = Path("artifacts/contract.json")

st.title("TimeTracker")


def load_contract() -> dict | None:
    if CONTRACT_FILE.exists():
        with open(CONTRACT_FILE, "r") as f:
            return json.load(f)
    return None


if "page" not in st.session_state:
    st.session_state.page = "home"


contract = load_contract()


# HOME PAGE
if st.session_state.page == "home":
    if contract is None:
        button_label = "+ Create new contract"
    else:
        button_label = "Adapt contract"

    if st.button(button_label):
        st.session_state.page = "contract"
        st.rerun()

    st.divider()

    st.subheader("Create work entry")

    working_date = st.date_input("Working date")
    start_time = st.time_input("Start time")
    end_time = st.time_input("End time")

    if st.button("Save work entry"):
        create_work_entry(
            str(working_date),
            start_time.strftime("%H:%M"),
            end_time.strftime("%H:%M"),
        )

        st.success("Work entry saved.")


# CONTRACT PAGE
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