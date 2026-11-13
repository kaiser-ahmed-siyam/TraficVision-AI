"""Dashboard configuration controls."""


def render_settings(settings):
    import streamlit as st

    st.subheader("Configuration")
    st.json({
        "model": settings.model.name,
        "confidence": settings.model.confidence,
        "IoU": settings.model.iou,
        "image_size": settings.model.image_size,
        "tracking": settings.tracking.algorithm,
        "live_inputs_enabled": settings.live_inputs_enabled,
    })
