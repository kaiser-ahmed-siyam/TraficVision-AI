"""Dashboard metric cards."""


def render_metrics(statistics):
    import streamlit as st

    by_class = statistics.get("by_class", {})
    columns = st.columns(4)
    columns[0].metric("Total vehicles", statistics.get("total_vehicles", 0))
    columns[1].metric("Vehicles / minute", f"{statistics.get('vehicles_per_minute', 0):.1f}")
    columns[2].metric("Cars", by_class.get("car", 0))
    columns[3].metric("Motorcycles", by_class.get("motorcycle", 0))
