"""Session-history table."""


def render_history(repository):
    import streamlit as st

    st.subheader("Session history")
    if repository is None:
        st.info("Session history is unavailable until a database is configured.")
        return
    st.dataframe(repository.list_sessions(), use_container_width=True)
