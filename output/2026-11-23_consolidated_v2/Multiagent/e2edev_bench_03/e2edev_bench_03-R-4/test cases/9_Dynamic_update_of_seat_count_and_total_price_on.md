# Dynamic update of seat count and total price on seat selection and deselection

Case ID · G-009

Requirements · e2edev\_bench\_03-R-4

Verify that clicking available seats toggles their selection state, updates the selected seat count at data-testid='selected-count', and recalculates the total price at data-testid='total-price' based on the current movie price. Also verify that deselecting a seat decreases the count and total price accordingly.
