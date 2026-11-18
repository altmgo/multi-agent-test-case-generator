# Edge and Error Handling for Missing or Zero Numeric Inputs

Case ID · G-040

Requirements · e2edev\_bench\_42-R-1, e2edev\_bench\_42-R-4, e2edev\_bench\_42-R-5, e2edev\_bench\_42-R-6, e2edev\_bench\_42-R-7, e2edev\_bench\_42-R-8, e2edev\_bench\_42-R-9, e2edev\_bench\_42-R-10, e2edev\_bench\_42-R-11

Verify that when numeric input fields or overtime hours are left empty or set to zero, the system gracefully defaults to zero for calculations, displaying appropriate fallback values like '-$0.00' for tax deductions and '$0.00' for earnings without throwing errors.
