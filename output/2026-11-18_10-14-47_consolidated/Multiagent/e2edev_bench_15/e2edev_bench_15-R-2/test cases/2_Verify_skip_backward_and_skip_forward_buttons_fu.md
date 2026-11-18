# Verify skip backward and skip forward buttons functionality and boundary limits

Case ID · G-002

Requirements · e2edev\_bench\_15-R-2

Verify that clicking Skip Backward data-testid='skip-backward-button' rewinds the video by 10 seconds and Skip Forward data-testid='skip-forward-button' fast-forwards by 25 seconds using data-skip attributes. Ensure currentTime never drops below 0 or exceeds the video's total duration.
