# Add a single product to cart via drag-and-drop

Case ID · G-045

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

User drags a product list item (e.g., data-testid="product-item-1") from the product list and drops it into the designated drop area (id="div1"). The system captures the product title and price, updates the cart display showing the title in .box2, unit price in .box3, quantity as 1 in .box1, and recalculates the total price displayed in <div id="allMoney"> with correct currency formatting.
