# Missing draggable attribute prevents drag initiation

Case ID · G-051

Requirements · e2edev\_bench\_01-R-1

Remove the 'draggable="true"' attribute from a product <li> element and attempt to drag it. Verify that no dragstart event is fired and the product title and price are not captured, causing the drop area to receive no data.
