# e2edev\_bench\_08-R-3

The system shall allow users to add a book to the library list using the form identified by my-library-form. The form includes three fields: 'User Name' (data-testid="user-name-input"), 'Book Name' (data-testid="book-name-input"), and 'Book Type', which includes the options 'Fiction' (data-testid="fiction-radio"), 'Programming' (data-testid="programming-radio"), and 'Cooking' (data-testid="cooking-radio").Upon clicking the 'Add Book' button (data-testid="add-book-button"), the system shall validate the inputs as follows:
1. If either the 'User Name' or 'Book Name' field is empty, the system shall display an error alert with the message "Oops! Book is not issued".
2. If the entered 'Book Name' has already been issued to another user, the system shall display an error alert with the message "Oops! Book is already issued by [issuedUser]".
3. If all inputs are valid and the book has not been issued, the system shall add the entry to the list, displaying the reader’s name, book name, and genre in the table. A success alert with the message "Success Book is issued" shall be shown.
The system shall also handle edge cases such as unusually long book names and ensure that the list persists across page reloads using local storage.
