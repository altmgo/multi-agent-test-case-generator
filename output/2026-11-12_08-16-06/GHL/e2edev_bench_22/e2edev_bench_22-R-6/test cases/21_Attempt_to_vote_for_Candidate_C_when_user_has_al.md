# Attempt to vote for Candidate C when user has already voted

Case ID · G-021

Requirements · e2edev\_bench\_22-R-3, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

User clicks vote-button-C when 'hasVoted' is present in localStorage. System prevents additional votes by displaying an alert with the message 'You've already voted!' and ensures total votes remain unchanged.
