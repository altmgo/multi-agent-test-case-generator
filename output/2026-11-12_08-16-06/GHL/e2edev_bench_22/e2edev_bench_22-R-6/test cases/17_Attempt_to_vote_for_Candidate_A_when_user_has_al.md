# Attempt to vote for Candidate A when user has already voted

Case ID · G-017

Requirements · e2edev\_bench\_22-R-1, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

User clicks vote-button-A when 'hasVoted' key is set to 'true' in localStorage. System triggers an alert with message 'You've already voted!' and makes no changes to vote counts or total votes.
