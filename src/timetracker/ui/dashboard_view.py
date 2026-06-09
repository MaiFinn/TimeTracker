from datetime import date

import pandas as pd
import streamlit as st
from timetracker.reports.monthly_report import build_monthly_report_rows, build_total_report_row

from timetracker.summary import (
    calculate_monthly_balance,
    calculate_total_balance_history,
    calculate_work_balance,
)

STATUS_OPTIONS = {
    "Worked": "worked",
    "Cancelled by employer": "cancelled_by_employer",
    "Cancelled by employee": "cancelled_by_employee",
}


def render_dashboard(
    contract: dict | None,
    work_entries: list[dict],
    month_names: list[str],
) -> None:
    """Render dashboard with balance metrics and chart."""

    if contract is None:
        st.info("Create a contract to see your working time balance.")
        return

    st.subheader("Working time balance")

    included_statuses = _render_status_filter()

    _render_total_balance(
        contract,
        work_entries,
        included_statuses,
    )

    _render_total_balance_chart(
        contract,
        work_entries,
        included_statuses,
    )

    st.divider()

    _render_month_selector(month_names)
    _render_monthly_balance(contract, work_entries, month_names, included_statuses)


def _render_status_filter() -> list[str]:
    """Render status filter and return included entry statuses."""

    #st.subheader("Included entry types")

    col1, col2, col3 = st.columns(3)

    with col1:
        include_worked = st.toggle(
            "🟢 Worked",
            value=True,
        )

    with col2:
        include_employer = st.toggle(
            "🔵 Cancelled by employer",
            value=False,
        )

    with col3:
        include_employee = st.toggle(
            "🔴 Cancelled by employee",
            value=False,
        )

    included_statuses = []

    if include_worked:
        included_statuses.append("worked")

    if include_employer:
        included_statuses.append("cancelled_by_employer")

    if include_employee:
        included_statuses.append("cancelled_by_employee")

    if not included_statuses:
        st.warning(
            "No entry type selected. Balance is calculated with 0 actual hours."
        )

    return included_statuses


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
    included_statuses: list[str],
) -> None:
    """Render total balance metrics."""

    total_balance = calculate_work_balance(
        contract,
        work_entries,
        included_statuses=included_statuses,
    )

    st.subheader("Working time balance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Actual hours", f"{total_balance['actual_hours']:.2f} h")
    col2.metric("Expected hours", f"{total_balance['expected_hours']:.2f} h")
    col3.metric("Balance", f"{total_balance['balance_hours']:.2f} h")


def _render_monthly_balance(
    contract: dict,
    work_entries: list[dict],
    month_names: list[str],
    included_statuses: list[str],
) -> None:
    """Render monthly balance metrics."""

    monthly_balance = calculate_monthly_balance(
        contract,
        work_entries,
        year=int(st.session_state.active_year),
        month=int(st.session_state.active_month),
        included_statuses=included_statuses,
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
    included_statuses: list[str],
) -> None:
    """Render total balance history chart."""

    import plotly.graph_objects as go

    contract_start_date = pd.to_datetime(contract["start_date"]).date()
    today = date.today()

    #st.subheader("Total balance over time")

    #st.caption("Displayed balance period")

    col1, col2 = st.columns(2)

    with col1:
        chart_start_date = st.date_input(
            "From",
            value=contract_start_date,
        )

    with col2:
        chart_end_date = st.date_input(
            "To",
            value=today,
        )

    balance_history = calculate_total_balance_history(
        contract,
        work_entries,
        start_date=chart_start_date,
        end_date=chart_end_date,
        included_statuses=included_statuses,
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

    work_entry_markers = []

    for entry in work_entries:
        entry_date = pd.to_datetime(entry["date"])

        if entry_date < pd.to_datetime(chart_start_date) or entry_date > pd.to_datetime(chart_end_date):
            continue

        if entry_date not in balance_chart_data.index:
            continue

        status = entry.get("entry_status", "worked")

        if status not in included_statuses:
            continue

        work_entry_markers.append(
            {
                "date": entry_date,
                "balance": balance_chart_data.loc[entry_date, "balance"],
                "status": status,
                "total_time": entry["total_time"],
            }
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=balance_chart_data.index,
            y=balance_chart_data["balance"],
            mode="lines",
            name="Balance",
            line=dict(width=3),
        )
    )

    fig.add_hline(
        y=0,
        line_width=4,
        line_color="black",
    )

    positive = balance_chart_data["balance"].clip(lower=0)
    negative = balance_chart_data["balance"].clip(upper=0)

    fig.add_trace(
        go.Scatter(
            x=balance_chart_data.index,
            y=positive,
            fill="tozeroy",
            fillcolor="rgba(0,180,0,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=balance_chart_data.index,
            y=negative,
            fill="tozeroy",
            fillcolor="rgba(220,0,0,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
        )
    )

    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=20, b=0),
    )

    if work_entry_markers:
        marker_data = pd.DataFrame(work_entry_markers)

        marker_symbols = {
            "worked": "diamond",
            "cancelled_by_employer": "circle",
            "cancelled_by_employee": "x",
        }

        marker_colors = {
            "worked": "#2E7D32",
            "cancelled_by_employer": "#1565C0",
            "cancelled_by_employee": "#C62828",
        }

        for status, group in marker_data.groupby("status"):
            fig.add_trace(
                go.Scatter(
                    x=group["date"],
                    y=group["balance"],
                    mode="markers",
                    name=status.replace("_", " "),
                    marker=dict(
                        size=13,
                        symbol=marker_symbols.get(status, "circle"),
                        color=marker_colors.get(status, "#2E7D32"),
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate=(
                        "<b>%{x|%Y-%m-%d}</b><br>"
                        "Status: " + status.replace("_", " ") + "<br>"
                        "Duration: %{customdata}<br>"
                        "Balance: %{y:.2f} h"
                        "<extra></extra>"
                    ),
                    customdata=group["total_time"],
                )
            )

    st.plotly_chart(
        fig,
        width="stretch",
    )

def _render_report_export(
    contract: dict,
    work_entries: list[dict],
) -> None:
    """Render report export button."""

    rows = build_monthly_report_rows(contract, work_entries)
    rows.append(build_total_report_row(contract, work_entries))

    report_data = pd.DataFrame(rows)
    csv_data = report_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download full report CSV",
        data=csv_data,
        file_name="timetracker_report.csv",
        mime="text/csv",
    )