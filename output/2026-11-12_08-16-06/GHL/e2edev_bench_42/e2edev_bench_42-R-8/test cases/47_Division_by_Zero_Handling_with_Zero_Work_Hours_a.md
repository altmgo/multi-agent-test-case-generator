# Division by Zero Handling with Zero Work Hours and Workdays

Case ID · G-047

Requirements · e2edev\_bench\_42-R-7, e2edev\_bench\_42-R-8

Set both work hours per day (data-testid='work-hour-input') and workdays per week (data-testid='work-week-input') to zero while supplying a valid gross salary, then calculate. Verify the system handles this edge/error condition gracefully without crashing, displaying $0.00 or placeholder values for hourly and daily salaries.
