# e2edev\_bench\_05-R-2

The system must allow users to interact with the search functionality on the 'Dictionary' webpage. When the search input field, identified by data-testid 'search-input', is empty and the user clicks the 'Search' button (data-testid 'search-button'), a toast notification with data-testid 'error-toast' should be displayed, containing the message "ERROR: Please type the word to be searched...". If the search input contains a valid word, the error toast should not be shown, ensuring the user is only prompted when necessary.
