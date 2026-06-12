import streamlit as st

from timetracker.config.paths import DATABASE_FILE
from timetracker.security import hash_password
from timetracker.storage.user_storage import (
    authenticate_user,
    create_user,
    get_user_by_username,
)


def render_login_page() -> None:
    """Render login and account creation page."""

    st.subheader("Login")

    tab_login, tab_register = st.tabs(["Login", "Create account"])

    with tab_login:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = authenticate_user(
                DATABASE_FILE,
                username,
                password,
            )

            if user is None:
                st.error("Invalid username or password.")
                return

            st.session_state.user_id = user["id"]
            st.session_state.username = user["username"]
            st.rerun()

    with tab_register:
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password",
        )

        if st.button("Create account"):
            if not new_username or not new_password:
                st.error("Username and password are required.")
                return

            existing_user = get_user_by_username(
                DATABASE_FILE,
                new_username,
            )

            if existing_user is not None:
                st.error("Username already exists.")
                return

            user_id = create_user(
                DATABASE_FILE,
                new_username,
                hash_password(new_password),
            )

            st.session_state.user_id = user_id
            st.session_state.username = new_username
            st.rerun()


def render_logout_button() -> None:
    """Render logout button."""

    if st.button("Logout"):
        st.session_state.pop("user_id", None)
        st.session_state.pop("username", None)
        st.rerun()