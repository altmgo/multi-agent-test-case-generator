# Cast vote for Candidate C when user has not voted yet

Case ID · G-020

Requirements · e2edev\_bench\_22-R-3, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

User clicks vote-button-C when 'hasVoted' key is absent. System increments Candidate C vote count, updates total-votes, saves 'hasVoted' in localStorage, and shows confirmation message 'Thank you for voting for Candidate C!' which fades out after 3 seconds.
