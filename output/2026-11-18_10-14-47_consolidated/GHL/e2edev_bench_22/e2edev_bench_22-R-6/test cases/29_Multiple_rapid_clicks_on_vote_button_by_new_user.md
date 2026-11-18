# Multiple rapid clicks on vote button by new user

Case ID · G-029

Requirements · e2edev\_bench\_22-R-1, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

Simulate rapid consecutive clicks on 'vote-button-A' by a user who has not yet voted to test if race conditions allow multiple increments or multiple conflicting confirmation messages before localStorage sets the 'hasVoted' flag.
