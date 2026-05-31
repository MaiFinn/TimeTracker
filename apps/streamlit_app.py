from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st

from timetracker.storage.json_storage import load_json
from timetracker.ui.contract_view import render_contract_page
from timetracker.ui.work_entry_view import render_work_entry_page
from timetracker.summary import (
    calculate_daily_actual_hours,
    calculate_monthly_balance,
    calculate_work_balance,
)

CONTRACT_FILE = Path("artifacts/contract.json")
WORK_ENTRIES_FILE = Path("artifacts/work_entries.json")

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

MONTH_NAMES = list(MONTHS.keys())

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

    if contract is not None:
        selected_year = st.number_input(
            "Year",
            min_value=2000,
            max_value=2100,
            value=int(st.session_state.active_year),
            step=1,
            key=f"year_selector_{st.session_state.active_year}_{st.session_state.active_month}",
        )

        selected_month_name = st.selectbox(
            "Month",
            options=MONTH_NAMES,
            index=int(st.session_state.active_month) - 1,
            key=f"month_selector_{st.session_state.active_year}_{st.session_state.active_month}",
        )

        selected_month = MONTHS[selected_month_name]

        if (
            int(selected_year) != st.session_state.active_year
            or selected_month != st.session_state.active_month
        ):
            st.session_state.active_year = int(selected_year)
            st.session_state.active_month = selected_month
            st.session_state.selected_date = None
            st.session_state.selected_entry_id = None
            st.rerun()

        total_balance = calculate_work_balance(contract, work_entries)

        monthly_balance = calculate_monthly_balance(
            contract,
            work_entries,
            year=int(st.session_state.active_year),
            month=int(st.session_state.active_month),
        )

        active_month_name = MONTH_NAMES[int(st.session_state.active_month) - 1]

        st.subheader("Total balance")

        col1, col2, col3 = st.columns(3)
        col1.metric("Actual hours", f"{total_balance['actual_hours']:.2f} h")
        col2.metric("Expected hours", f"{total_balance['expected_hours']:.2f} h")
        col3.metric("Balance", f"{total_balance['balance_hours']:.2f} h")

        st.subheader(
            f"Monthly balance: {active_month_name} {int(st.session_state.active_year)}"
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Actual hours", f"{monthly_balance['actual_hours']:.2f} h")
        col2.metric("Expected hours", f"{monthly_balance['expected_hours']:.2f} h")
        col3.metric("Balance", f"{monthly_balance['balance_hours']:.2f} h")

        balance_value = monthly_balance["balance_hours"]

        if balance_value >= 0:
            st.success(f"Monthly balance is positive: +{balance_value:.2f} h")
        else:
            st.error(f"Monthly balance is negative: {balance_value:.2f} h")

        daily_hours = calculate_daily_actual_hours(work_entries)

        if daily_hours:
            chart_data = pd.DataFrame(
                {
                    "date": list(daily_hours.keys()),
                    "hours": list(daily_hours.values()),
                }
            )

            chart_data["date"] = pd.to_datetime(chart_data["date"])
            chart_data = chart_data.sort_values("date")
            chart_data = chart_data.set_index("date")

            st.subheader("Worked hours over time")
            st.line_chart(chart_data)
        else:
            st.info("No work entries available for chart.")

    else:
        st.info("Create a contract to see your working time balance.")

    st.divider()

    render_work_entry_page(
        selected_year=int(st.session_state.active_year),
        selected_month=int(st.session_state.active_month),
    )


elif st.session_state.page == "contract":
    render_contract_page(contract)