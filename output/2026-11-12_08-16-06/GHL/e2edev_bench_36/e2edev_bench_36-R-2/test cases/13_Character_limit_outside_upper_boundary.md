# Character limit outside upper boundary

Case ID · G-013

Requirements · e2edev\_bench\_36-R-1, e2edev\_bench\_36-R-2

Set the character limit input to 5000 via data-testid='char-limit' and enter 5001 characters in data-testid='text-input'. Verify that the character count visually indicates excess by changing text color to red in data-testid='char-count'.
