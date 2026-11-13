"""Dashboard charts and CSV export."""


def render_analytics(statistics, events):
    import streamlit as st

    from analytics.charts import class_distribution_figure, direction_figure
    from analytics.report_generator import events_to_csv

    st.subheader("Traffic analytics")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(class_distribution_figure(statistics), use_container_width=True)
    with right:
        st.plotly_chart(direction_figure(statistics), use_container_width=True)
    st.download_button("Download traffic report", events_to_csv(events), "traffic_report.csv", "text/csv")
