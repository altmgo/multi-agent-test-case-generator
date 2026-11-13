# e2edev\_bench\_10-R-3

When the user accesses the 'Online Quiz Portal' page, the system dynamically generates answer options for the current question, displaying them as radio buttons within the <div> element (data-testid: 'options'). Each option is a radio input with a unique value matching the option text, a label showing the text, and a shared name attribute 'option' to allow single selection. The system updates the radio buttons for each question based on the quizData array.
