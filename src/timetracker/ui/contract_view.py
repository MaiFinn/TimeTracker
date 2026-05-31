from datetime import datetime
import streamlit as st

from timetracker.contract_handler import create_contract


def render_contract_page(contract: dict | None) -> None:
    """Render the contract page."""

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