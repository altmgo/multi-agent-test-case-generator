# Update existing timetable entry when adding a duplicate time range

Case ID · G-038

Requirements · e2edev\_bench\_18-R-6, e2edev\_bench\_18-R-8

Add a timetable entry, then submit a new entry with the exact same time range but a different subject and selected days. Verify that the system updates the existing cells for the selected days with the new subject name instead of creating a new row, and resets the form.
