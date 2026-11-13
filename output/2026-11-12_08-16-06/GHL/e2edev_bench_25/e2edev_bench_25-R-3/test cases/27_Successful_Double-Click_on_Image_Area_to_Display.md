# Successful Double-Click on Image Area to Display Heart and Increment Likes

Case ID · G-027

Requirements · e2edev\_bench\_25-R-1, e2edev\_bench\_25-R-3, e2edev\_bench\_25-R-5

Verify that upon page load the instruction text is visible with data-testid='instruction-text', and when a user double-clicks inside the image container (data-testid='image-container' and class 'loveMe'), a heart icon (<i> with classes 'fas fa-heart') is dynamically displayed at the exact relative click coordinates. Verify that the like count in data-testid='times' increments by 1 and the heart icon automatically disappears after 1 second.
