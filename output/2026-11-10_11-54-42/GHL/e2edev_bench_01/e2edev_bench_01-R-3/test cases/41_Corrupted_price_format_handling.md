# Corrupted price format handling

Case ID · G-041

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

Change product-item-4 price element to an invalid string "$abc". Drag and drop into drop-area. Verify that the cart shows the title, but total calculation either skips the item or displays an error indicator, and allMoney does not show NaN.
