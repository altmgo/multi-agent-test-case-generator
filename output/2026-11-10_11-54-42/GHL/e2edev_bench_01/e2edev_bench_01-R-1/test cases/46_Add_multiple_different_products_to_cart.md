# Add multiple different products to cart

Case ID · G-046

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

User sequentially drags several distinct product items (e.g., data-testid="product-item-1" and data-testid="product-item-2") into the drop area. After each drop, the cart updates to list each product title, its unit price, quantity=1, and the total price in <div id="allMoney"> reflects the sum of all individual prices, formatted to two decimal places with the currency symbol.
