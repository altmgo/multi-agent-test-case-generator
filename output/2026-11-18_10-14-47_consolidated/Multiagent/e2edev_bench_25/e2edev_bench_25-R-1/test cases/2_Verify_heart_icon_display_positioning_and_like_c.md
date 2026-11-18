# Verify heart icon display, positioning, and like count increment on double-click

Case ID · G-002

Requirements · e2edev\_bench\_25-R-1, e2edev\_bench\_25-R-3

Double-click inside the image area (data-testid='image-container' and class 'loveMe') and verify that a heart icon (<i> element with classes 'fas' and 'fa-heart') is displayed at the exact relative click coordinates, the like count in data-testid='times' increments by 1, and the heart icon automatically disappears after 1 second.
