# Markdown rendering and invalid markdown handling

Case ID · G-002

Requirements · e2edev\_bench\_02-R-2

Preconditions: A note is in edit mode with a visible textarea (data-testid='note-textarea'). Action: Type Markdown content or invalid Markdown (e.g., unmatched **) and exit edit mode using the 'Edit' button (data-testid='edit-note-button'). Expected Behavior: Valid Markdown renders in the main display area (data-testid='note-main'), invalid Markdown does not crash and displays raw input, and changes persist in local storage.
