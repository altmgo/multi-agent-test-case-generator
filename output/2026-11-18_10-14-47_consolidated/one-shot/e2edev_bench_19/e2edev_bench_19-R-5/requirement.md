# e2edev\_bench\_19-R-5

Upon loading the todo list page, the system must retrieve the todos from localStorage using the 'todos' key. Each todo item is displayed as a list item (<li>) within the unordered list with data-testid='todo-list'. The completion status is reflected by the presence or absence of the 'completed' class on the list item. If a todo is completed in localStorage, the 'completed' class is applied; otherwise, it is absent. If localStorage is empty, no items are displayed. The data should be parsed as JSON to reconstruct the list.
