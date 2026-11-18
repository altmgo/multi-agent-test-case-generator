# Rapid Consecutive Double-Clicks and Boundary Handling

Case ID · G-028

Requirements · e2edev\_bench\_25-R-1, e2edev\_bench\_25-R-3

Verify that when multiple double-clicks occur in rapid succession within the maximum interval of 800 milliseconds, multiple heart icons are correctly created at their respective click locations (including near the boundaries of the image area) and each is removed from the DOM after exactly 1 second, while the like count updates correctly for each successful double-click.
