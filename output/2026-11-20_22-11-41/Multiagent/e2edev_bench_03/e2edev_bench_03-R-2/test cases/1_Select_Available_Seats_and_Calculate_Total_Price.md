# Select Available Seats and Calculate Total Price

Case ID · G-001

Requirements · e2edev\_bench\_03-R-1, e2edev\_bench\_03-R-2, e2edev\_bench\_03-R-4, e2edev\_bench\_03-R-5

Precondition: Webpage is loaded. Steps: Click an available seat without the occupied class and select a movie from data-testid="movie-select". Expected: The seat is marked as selected, data-testid="selected-count" increments, and data-testid="total-price" updates correctly based on the number of selected seats multiplied by the movie price.
