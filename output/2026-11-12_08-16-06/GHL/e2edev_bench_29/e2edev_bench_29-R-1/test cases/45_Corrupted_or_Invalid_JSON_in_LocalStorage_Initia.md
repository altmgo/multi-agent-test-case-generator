# Corrupted or Invalid JSON in LocalStorage Initialization

Case ID · G-045

Requirements · e2edev\_bench\_29-R-1, e2edev\_bench\_29-R-8

Manually inject malformed or non-JSON data into the browser's localStorage under the 'transactions' key, then load the application. Verify that the application handles the parsing failure gracefully, defaults to empty values ($0.00), and does not crash.
