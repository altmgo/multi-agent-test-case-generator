# Dynamic update of total price and seat count upon seat and movie selection

Case ID · G-001

Requirements · e2edev\_bench\_03-R-1

Verify that clicking an available seat marks it as selected and updates the selected seat count (data-testid=selected-count), and that selecting a movie from the dropdown (data-testid=movie-select) updates the total price (data-testid=total-price) calculated as selected seats multiplied by the movie price, while occupied seats remain non-selectable and changing the movie updates the total price accordingly.
