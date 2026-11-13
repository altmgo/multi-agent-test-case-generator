# Simultaneous drag of two items \(abnormal\)

Case ID · G-043

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3

Begin dragging product-item-1, then without releasing, start dragging product-item-2. Release both over drop-area. Expect the system to process only the first drag event; the second should be ignored, resulting in a single item added and total reflecting only the first product.
