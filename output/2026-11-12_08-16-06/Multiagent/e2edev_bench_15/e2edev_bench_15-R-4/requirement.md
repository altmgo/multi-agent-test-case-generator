# e2edev\_bench\_15-R-4

The Playback Rate slider (data-testid='playback-rate-slider') lets users adjust video speed from 0.5x to 2x in 0.05 steps. Changing the slider updates the video’s playback rate in real time via the handleRangeUpdate function. Values outside the range (e.g. 3) are rejected, and the video keeps playing at the last valid speed. The slider starts at 1x and is implemented as a range input with min 0.5, max 2, and default value 1.
