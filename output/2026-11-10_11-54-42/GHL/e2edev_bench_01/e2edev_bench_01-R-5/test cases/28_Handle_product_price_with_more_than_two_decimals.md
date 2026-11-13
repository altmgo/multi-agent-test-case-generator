# Handle product price with more than two decimals

Case ID · G-028

Requirements · e2edev\_bench\_01-R-5

State: Dragging a product whose price contains more than two decimal places (e.g., $12.345). Event: drop into the cart. Transition: system rounds/format the price to two decimals ($12.35) before storing and includes it in total calculation displayed in #allMoney. Requirement IDs: ["e2edev_bench_01-R-5"].
