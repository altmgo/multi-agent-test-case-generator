# Verify skip boundaries for duration and zero seconds

Case ID · G-004

Requirements · e2edev\_bench\_15-R-2

Verify that skipping backward when currentTime is less than 10 seconds does not result in a negative currentTime (clamps to 0), and skipping forward past the video's duration does not exceed it.
