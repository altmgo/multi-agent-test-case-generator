# Sequential drag‑drop of multiple distinct products

Case ID · G-034

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

Condition: three different product items, each draggable with valid title and price; drop area exists; each product dropped sequentially. Action: for each drop, system captures title and price (R-1), adds a new entry to cart updating .box1, .box2, .box3 (R-3), and after all drops recalculates total price reflecting sum of three items (R-5).
