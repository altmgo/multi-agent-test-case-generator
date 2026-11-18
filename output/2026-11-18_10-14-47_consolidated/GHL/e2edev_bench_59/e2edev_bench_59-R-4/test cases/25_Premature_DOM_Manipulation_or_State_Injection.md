# Premature DOM Manipulation or State Injection

Case ID · G-025

Requirements · e2edev\_bench\_59-R-4, e2edev\_bench\_59-R-5

Simulate error conditions where user tries to trigger submission or quiz reset actions out of order, or inject invalid values into the score display element (data-testid='quiz'). Verify that the final score formatting strictly follows 'You answered X/Y questions correctly' and handles completion safely.
