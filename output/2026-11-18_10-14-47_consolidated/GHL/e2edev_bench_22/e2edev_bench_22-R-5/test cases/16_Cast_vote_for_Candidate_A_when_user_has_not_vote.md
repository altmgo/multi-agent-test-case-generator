# Cast vote for Candidate A when user has not voted yet

Case ID · G-016

Requirements · e2edev\_bench\_22-R-1, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

User clicks vote-button-A when 'hasVoted' key is absent from localStorage. System increments Candidate A vote count, updates total-votes, sets 'hasVoted' in localStorage, displays confirmation message for Candidate A that fades out after 3 seconds, and updates results-chart.
