# Rapid Consecutive Clicks on Get Another Joke Button

Case ID · G-007

Requirements · e2edev\_bench\_12-R-2, e2edev\_bench\_12-R-3

Perform rapid, multiple consecutive clicks on the 'Get Another Joke' button (data-testid='get-another-joke-button') before the previous asynchronous fetch request completes, to test for race conditions and proper replacement of the joke container (data-testid='joke').
