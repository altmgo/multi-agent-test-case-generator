# Verify job title handling including long strings and special characters

Case ID · G-003

Requirements · e2edev\_bench\_42-R-3, e2edev\_bench\_42-R-7

Enter a very long job title containing special characters into the 'Job' input field (data-testid='job-input') and calculate salary. Verify that the job title is displayed correctly without truncation or formatting issues in both the overview title and results section. Additionally, verify that leaving the field empty defaults the display to '______'.
