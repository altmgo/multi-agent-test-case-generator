# e2edev\_bench\_08-R-5

Upon loading the Library Management System webpage, the system must retrieve the list of books stored in the browser's local storage and display them within the table body element identified by data-testid="table-body". If local storage contains one or more entries, each book must be rendered with its full details, including serial number, date of issue, reader's name, book name, and genre. If local storage is empty, the table body should remain empty to indicate no books are currently stored. The data must be stored under the listItems key as a JSON string representing an array of objects, each with userName, bookName, and type fields. For example:
localStorage.setItem('listItems', JSON.stringify([{ userName: 'John Doe', bookName: 'Python Programming', type: 'Programming' }])).
The system must parse and display this data as if it were submitted through the form.


