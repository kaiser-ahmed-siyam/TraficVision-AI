"""Streamlit sidebar controls."""


def render_sidebar(settings):
    import streamlit as st

    with st.sidebar:
        st.header("TrafficVision AI")
        st.caption("Vehicle detection & traffic analytics")
        page = st.radio("Navigation", ["Dashboard", "Video Analysis", "Live Monitor", "Analytics", "Settings", "History"])
        st.divider()
        st.caption(f"Environment: {settings.application.environment}")
    return page
