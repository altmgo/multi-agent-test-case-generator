# Total price rounding error for large sums

Case ID · G-055

Requirements · e2edev\_bench\_01-R-5

Add several high‑price products so the cart total exceeds $999.99. Check that the total displayed in #allMoney is correctly rounded to two decimals and includes the currency symbol; any truncation or locale‑specific formatting constitutes a defect.
