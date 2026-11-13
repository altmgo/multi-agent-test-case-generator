# Drop area absent during drag‑drop

Case ID · G-033

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3

Condition: product element is draggable with valid title and price; drop area element with id='div1' is not present in DOM. Action: drag event captures data (R-1) but drop cannot be completed; system rejects drop and does not update cart or total (fails R-3, R-5).
