# Non-draggable element does not trigger drag logic

Case ID · G-006

Requirements · e2edev\_bench\_01-R-1

Attempting to drag an element that lacks draggable="true" (e.g., a plain <div>) does not fire a dragstart event and no dataTransfer payload is created.
