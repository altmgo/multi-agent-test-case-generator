# Load notes from localStorage on startup

Case ID · G-005

Requirements · e2edev\_bench\_02-R-5

Preconditions: Notes are populated in localStorage or localStorage is empty. Action: Load the Notes App webpage. Expected Behavior: The app retrieves saved notes, dynamically creating note elements with tools, main div, and textarea. Notes with content show the main div with hidden textarea, empty notes show the textarea with hidden main div, and an empty localStorage results in no notes shown.
