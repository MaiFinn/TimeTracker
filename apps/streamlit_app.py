import streamlit as st

from timetracker.work_entry_handler import create_work_entry

st.title("TimeTracker")

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