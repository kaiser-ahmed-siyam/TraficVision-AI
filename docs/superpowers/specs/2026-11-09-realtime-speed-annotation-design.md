# Real-time annotation and speed tracking design

## Intent

Show annotated frames while processing instead of waiting for the output video, and display a per-track speed estimate beside each vehicle. The same annotation path must work for uploaded videos and local webcam/RTSP monitoring.

## Decisions

- Use the existing bottom-center track anchor and timestamped frame stream.
- Estimate speed from pixel displacement divided by a configurable `pixels_per_meter` calibration, convert m/s to km/h, and smooth over a short window.
- Display `ID`, class, and speed in the tracking overlay; the pipeline also returns speed estimates for analytics/UI use.
- Use Streamlit placeholders and progress callbacks for uploaded videos.
- Keep webcam/RTSP local-only and run them through the same `TrafficPipeline`.
- Default calibration is deliberately explicit and approximate; users must tune it for their camera geometry.

## Non-goals

- No claim of radar-grade or legally enforceable speed accuracy.
- No camera calibration wizard or perspective transformation in this change.
