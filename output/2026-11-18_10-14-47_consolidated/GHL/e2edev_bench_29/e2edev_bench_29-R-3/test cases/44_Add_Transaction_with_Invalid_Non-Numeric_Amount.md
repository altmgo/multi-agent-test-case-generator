# Add Transaction with Invalid Non-Numeric Amount Data

Case ID · G-044

Requirements · e2edev\_bench\_29-R-3, e2edev\_bench\_29-R-5

Attempt to input non-numeric text (e.g., 'abc') into the 'amount-input' field alongside a valid description, then click the add button. Verify that the validation fails, displays the error alert, and prevents the transaction from being added.
