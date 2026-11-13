# e2edev\_bench\_15-R-5

The progress bar visually tracks the video’s playback progress by dynamically updating the width of the .progress__filled element based on the formula (video.currentTime / video.duration) * 100. It begins filling when playback starts (triggered via the data-testid='toggle-play-button'), reaches 100% upon video completion, and resets to 0% when the video restarts. Users can scrub manually by clicking or dragging on the .progress element, with real-time updates to both the video's currentTime and the progress bar's fill.
