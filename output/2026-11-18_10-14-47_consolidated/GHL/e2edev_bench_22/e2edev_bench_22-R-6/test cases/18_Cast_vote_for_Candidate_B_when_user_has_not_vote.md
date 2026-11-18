# Cast vote for Candidate B when user has not voted yet

Case ID · G-018

Requirements · e2edev\_bench\_22-R-2, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

User clicks vote-button-B when 'hasVoted' key is absent from localStorage. System increments Candidate B vote count, updates total-votes, sets 'hasVoted' in localStorage, displays temporary confirmation message 'Thank you for voting for Candidate B!', and updates results-chart.
