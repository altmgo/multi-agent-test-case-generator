# e2edev\_bench\_24-R-6

When the user presses the Enter key while focused on any input field, the system shall compute the compound interest based on the provided inputs and display the result in the 'Result' section. The system shall validate all inputs to ensure they are positive numeric values greater than zero. If any input is invalid (e.g., empty, non-numeric, or negative), an alert with the message 'Please Enter Valid Values!!' shall be displayed, and the 'Result' section shall remain unchanged, displaying '0'. The calculation shall use the formula: CI = Principal * (1 + (Interest Rate / (Number of Times in Year * 100)))^(Number of Times in Year * Number of Years), rounded to two decimal places. The following UI elements and attributes are involved: 

- Input fields:
  - Principal: [data-testid='principal']
  - Interest Rate (%): [data-testid='annual-interest-rate']
  - Number of Years: [data-testid='number-of-year']
  - Number of Times in a Single Year: [data-testid='number-of-times-in-year']

- Result section:
  - Result label: [data-testid='result-label']
  - Result value: [data-testid='result-value']

- Button:
  - Calculate button: [data-testid='calculate-button']

The Enter key functionality shall trigger the calculation regardless of which input field is focused, and the result shall be displayed in the 'Result' section with data-testid='result-value'.
