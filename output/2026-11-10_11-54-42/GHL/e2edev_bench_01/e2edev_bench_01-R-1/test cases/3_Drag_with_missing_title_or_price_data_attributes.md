# Drag with missing title or price data attributes

Case ID · G-003

Requirements · e2edev\_bench\_01-R-1

User drags a product <li> that lacks either the data-testid for title or price. The drag event should still fire but the transferred data should be incomplete, allowing the system to handle the error gracefully.
