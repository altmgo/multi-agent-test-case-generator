# Invalid product data does not break total calculation

Case ID · G-010

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-5

Simulate a product item with missing price attribute and drop it; verify that the system either ignores the item or handles the missing price gracefully without crashing, and total price reflects only valid items.
