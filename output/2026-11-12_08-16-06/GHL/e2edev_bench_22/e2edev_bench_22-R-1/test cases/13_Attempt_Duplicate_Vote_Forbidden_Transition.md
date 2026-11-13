# Attempt Duplicate Vote \(Forbidden Transition\)

Case ID · G-013

Requirements · e2edev\_bench\_22-R-1, e2edev\_bench\_22-R-2, e2edev\_bench\_22-R-3, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

Attempt to click any vote button when the 'hasVoted' key is already set to 'true' in localStorage. Verifies that an alert with 'You've already voted!' triggers and vote counts remain completely unchanged.
