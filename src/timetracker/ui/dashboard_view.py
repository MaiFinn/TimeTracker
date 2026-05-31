from datetime import date

import pandas as pd
import streamlit as st

from timetracker.summary import (
    calculate_monthly_balance,
    calculate_total_balance_history,
    calculate_work_balance,
)


def render_dashboard(
    contract: dict | None,
    work_entries: list[dict],
    month_names: list[str],
) -> None:
    """Render dashboard with balance metrics and chart."""

    if contract is None:
        st.info("Create a contract to see your working time balance.")
        return

    _render_month_selector(month_names)
    _render_total_balance(contract, work_entries)
    _render_monthly_balance(contract, work_entries, month_names)
    _render_total_balance_chart(contract, work_entries)


def _render_month_selector(month_names: list[str]) -> None:
    """Render year and month selector."""

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
        options=month_names,
        index=int(st.session_state.active_month) - 1,
        key=f"month_selector_{st.session_state.active_year}_{st.session_state.active_month}",
    )

    selected_month = month_names.index(selected_month_name) + 1

    if (
        int(selected_year) != st.session_state.active_year
        or selected_month != st.session_state.active_month
    ):
        st.session_state.active_year = int(selected_year)
        st.session_state.active_month = selected_month
        st.session_state.selected_date = None
        st.session_state.selected_entry_id = None
        st.rerun()


def _render_total_balance(
    contract: dict,
    work_entries: list[dict],
) -> None:
    """Render total balance metrics."""

    total_balance = calculate_work_balance(contract, work_entries)

    st.subheader("Total balance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Actual hours", f"{total_balance['actual_hours']:.2f} h")
    col2.metric("Expected hours", f"{total_balance['expected_hours']:.2f} h")
    col3.metric("Balance", f"{total_balance['balance_hours']:.2f} h")


def _render_monthly_balance(
    contract: dict,
    work_entries: list[dict],
    month_names: list[str],
) -> None:
    """Render monthly balance metrics."""

    monthly_balance = calculate_monthly_balance(
        contract,
        work_entries,
        year=int(st.session_state.active_year),
        month=int(st.session_state.active_month),
    )

    active_month_name = month_names[int(st.session_state.active_month) - 1]

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


def _render_total_balance_chart(
    contract: dict,
    work_entries: list[dict],
) -> None:
    """Render total balance history chart."""

    contract_start_date = pd.to_datetime(contract["start_date"]).date()
    today = date.today()

    st.subheader("Total balance over time")

    chart_start_date = st.date_input(
        "Chart start date",
        value=contract_start_date,
    )

    chart_end_date = st.date_input(
        "Chart end date",
        value=today,
    )

    balance_history = calculate_total_balance_history(
        contract,
        work_entries,
        start_date=chart_start_date,
        end_date=chart_end_date,
    )

    if not balance_history:
        st.info("No data available for balance chart.")
        return

    balance_chart_data = pd.DataFrame(
        {
            "date": list(balance_history.keys()),
            "balance": list(balance_history.values()),
        }
    )

    balance_chart_data["date"] = pd.to_datetime(balance_chart_data["date"])
    balance_chart_data = balance_chart_data.sort_values("date")
    balance_chart_data = balance_chart_data.set_index("date")

    st.line_chart(balance_chart_data)