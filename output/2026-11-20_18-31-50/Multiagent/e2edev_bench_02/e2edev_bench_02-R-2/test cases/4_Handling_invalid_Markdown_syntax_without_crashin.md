# Handling invalid Markdown syntax without crashing

Case ID · G-004

Requirements · e2edev\_bench\_02-R-2

Verify that inputting invalid Markdown syntax (e.g., unmatched **) does not cause application errors or crashes, and upon exiting edit mode by clicking the "Edit" button (data-testid="edit-note-button"), the raw input is correctly displayed while changes persist in local storage.
