# Verify playback rate slider controls speed and rejects out-of-range values

Case ID · G-004

Requirements · e2edev\_bench\_15-R-4

Ensure the playback rate slider (data-testid='playback-rate-slider') modifies the video speed from 0.5x to 2x in 0.05 increments, starting at 1x. Verify that invalid values (e.g., 3) are rejected and the video maintains its last valid speed.
