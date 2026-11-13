# Drag and drop a new product with all attributes

Case ID · G-029

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

Condition: product element is draggable, has title and price attributes; drop area exists; drop performed; product not already in cart. Action: system initiates drag event capturing title and price (R-1), updates cart boxes .box1 (quantity=1), .box2 (title), .box3 (unit price) (R-3), recalculates total and displays in #allMoney (R-5).
