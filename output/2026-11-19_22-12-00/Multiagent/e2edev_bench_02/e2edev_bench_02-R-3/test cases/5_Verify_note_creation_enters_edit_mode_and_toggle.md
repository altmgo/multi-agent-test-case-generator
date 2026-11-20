# Verify note creation enters edit mode and toggles between view and edit modes

Case ID · G-005

Requirements · e2edev\_bench\_02-R-3

When a new note is created by clicking the Add note button (data-testid="add-note-button"), it immediately enters edit mode where the textarea (data-testid="note-textarea") is visible and the main content area (data-testid="note-main") is hidden. Clicking the Edit button (data-testid="edit-note-button") toggles the mode, hiding the textarea and displaying the formatted content in the main content area.
