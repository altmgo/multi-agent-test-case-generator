# Tampered localStorage 'hasVoted' flag with invalid value

Case ID · G-030

Requirements · e2edev\_bench\_22-R-2, e2edev\_bench\_22-R-5, e2edev\_bench\_22-R-6

Manually set the 'hasVoted' key in localStorage to a malformed string or a value other than 'true' (e.g., 'false', '1', or random text) and attempt to vote for Candidate B to verify if the system strictly checks for the presence and accurate state of the flag.
