# Add a repeated product and update quantity

Case ID · G-023

Requirements · e2edev\_bench\_01-R-3, e2edev\_bench\_01-R-5

State: CartUpdated with product A quantity N. Event: dragstart on the same product A and drop into the drop area. Transition: system stays in CartUpdated, increments quantity in .box1 to N+1, leaves title and unit price unchanged, and triggers total recalculation. Requirement IDs: ["e2edev_bench_01-R-3","e2edev_bench_01-R-5"].
