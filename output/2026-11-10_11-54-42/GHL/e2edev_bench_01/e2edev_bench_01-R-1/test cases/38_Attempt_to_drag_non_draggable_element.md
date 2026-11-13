# Attempt to drag non‑draggable element

Case ID · G-038

Requirements · e2edev\_bench\_01-R-1, e2edev\_bench\_01-R-3

Initiate a drag on a <div> without draggable="true" and drop it into drop-area. Expect no drag event, no cart update, and no change in total. System should ignore the action without error.
