# Verify overtime earnings and total earnings calculation

Case ID · G-008

Requirements · e2edev\_bench\_42-R-1, e2edev\_bench\_42-R-9, e2edev\_bench\_42-R-10, e2edev\_bench\_42-R-11

Input valid overtime hours per week and overtime rate per hour alongside salary parameters. Verify that overtime earnings are calculated by multiplying hours by rate by 4 (weeks per month), and that total earnings correctly sum the yearly net salary and total overtime earnings. Test edge cases such as zero overtime hours and negative values resulting in $0.00 overtime earnings.
