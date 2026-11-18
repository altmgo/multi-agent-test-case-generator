# Verify tax deduction calculation and negative value formatting

Case ID · G-005

Requirements · e2edev\_bench\_42-R-5, e2edev\_bench\_42-R-6

Input a gross salary and tax percentage, then click 'Calculate Salary'. Verify that the tax deduction is computed as (grossSalary * tax / 100) and displayed as a negative value. Test edge cases including zero gross salary, zero tax percentage, and negative tax percentages to ensure the output gracefully defaults or handles them correctly as '-$0.00'.
