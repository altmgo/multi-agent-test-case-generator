# Add the same product multiple times and verify quantity aggregation

Case ID · G-047

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

User drags the same product item (e.g., data-testid="product-item-1") repeatedly into the drop area. The cart should display a single entry for that product with the quantity incremented accordingly (e.g., quantity=3) in .box1, while .box2 and .box3 retain the title and unit price. The total price in <div id="allMoney"> must equal quantity × unit price, correctly formatted.
