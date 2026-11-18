# Delete Non-Existent Registration Index

Case ID · G-030

Requirements · e2edev\_bench\_20-R-8

Simulate clicking a delete button with an out-of-bounds index (e.g., 'delete-btn-0' when the table is empty) to verify that local storage and the UI do not throw unhandled exceptions or corrupt existing records.
