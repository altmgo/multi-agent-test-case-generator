# Add Transaction with Empty Description and Valid Amount

Case ID · G-042

Requirements · e2edev\_bench\_29-R-2, e2edev\_bench\_29-R-5

Attempt to add a transaction leaving the 'description-input' field completely blank while providing a valid amount in 'amount-input'. Verify that an alert with the message 'Please enter valid description and amount.' is shown and no transaction is added.
