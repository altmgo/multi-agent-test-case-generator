# Retrieve and render saved notes from localStorage on page load

Case ID · G-010

Requirements · e2edev\_bench\_02-R-5

When the Notes App webpage loads, it retrieves all saved notes from localStorage using JSON.parse(localStorage.getItem('notes')) and dynamically creates a div element with the class note for each stored note, containing a tools div with edit and delete buttons, a main div (data-testid="note-main"), and a textarea (data-testid="note-textarea").
