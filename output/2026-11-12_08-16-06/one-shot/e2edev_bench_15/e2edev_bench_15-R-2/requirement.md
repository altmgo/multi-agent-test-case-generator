# e2edev\_bench\_15-R-2

The video player allows users to rewind or fast-forward using the Skip Backward (data-testid='skip-backward-button') and Skip Forward (data-testid='skip-forward-button') buttons. Clicking Skip Backward rewinds by 10 seconds, and Skip Forward fast-forwards by 25 seconds. The buttons use data-skip attributes to adjust currentTime, ensuring it doesn't exceed the video's duration or go below 0 seconds.
