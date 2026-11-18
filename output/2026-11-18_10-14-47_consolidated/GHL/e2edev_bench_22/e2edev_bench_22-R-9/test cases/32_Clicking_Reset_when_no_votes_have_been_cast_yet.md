# Clicking Reset when no votes have been cast yet

Case ID · G-032

Requirements · e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6, e2edev\_bench\_22-R-9, e2edev\_bench\_22-R-11

Click the 'Reset' button (data-testid 'reset-button') when the application has zero votes and no 'hasVoted' flag in localStorage, verifying that the system handles the redundant reset gracefully without errors, clears state correctly, and still triggers the reset confirmation alert.
