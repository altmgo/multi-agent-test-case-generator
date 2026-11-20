# Graceful fallback for invalid Markdown syntax

Case ID · G-005

Requirements · e2edev\_bench\_02-R-2

Verify that when the user inputs invalid Markdown syntax such as unmatched bold markers (**), the application does not crash and displays the raw input when the user exits edit mode by clicking the "Edit" button (data-testid="edit-note-button"), while maintaining local storage updates.
