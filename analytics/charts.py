"""Plotly chart factories loaded only when charts are requested."""


def class_distribution_figure(statistics):
    import plotly.express as px

    by_class = statistics.get("by_class", {})
    return px.bar(x=list(by_class), y=list(by_class.values()), labels={"x": "Vehicle class", "y": "Count"}, title="Vehicles by class")


def direction_figure(statistics):
    import plotly.express as px

    by_direction = statistics.get("by_direction", {})
    return px.pie(names=list(by_direction), values=list(by_direction.values()), title="Crossing direction")
