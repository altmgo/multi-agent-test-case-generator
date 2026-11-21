# Mode switching and automatic saving

Case ID · G-003

Requirements · e2edev\_bench\_02-R-3

Preconditions: App page is loaded and a new note has been created. Action: Click the 'Edit' button (data-testid='edit-note-button') to toggle between edit and view modes while typing into the textarea. Expected Behavior: The note defaults to edit mode upon creation with textarea visible and main content hidden. Clicking the edit button toggles visibility between the textarea and main content area, and changes are automatically saved to local storage.
