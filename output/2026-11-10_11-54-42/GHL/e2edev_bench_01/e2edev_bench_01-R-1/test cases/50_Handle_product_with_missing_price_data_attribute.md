# Handle product with missing price data attribute

Case ID · G-050

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-5

User drags a product item whose price element is missing or malformed (e.g., no data-testid="product-price-1"). The drag event captures an undefined price; the cart should either display a placeholder or omit the price, and the total calculation must ignore the invalid entry or handle it without crashing. The test verifies that the system does not produce NaN or incorrect totals.
