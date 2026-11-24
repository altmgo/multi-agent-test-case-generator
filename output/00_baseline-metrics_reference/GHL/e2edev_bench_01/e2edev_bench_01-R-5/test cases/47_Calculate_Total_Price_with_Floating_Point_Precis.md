# Calculate Total Price with Floating Point Precision Errors

Case ID · G-047

Requirements · e2edev\_bench\_01-R-5

Test the total price calculation in <div id="allMoney"> when cart items have prices with multiple decimal places that could result in floating-point rounding inaccuracies (e.g., 10.10 + 20.20 + 30.30), ensuring the output is correctly formatted to exactly two decimal places.
