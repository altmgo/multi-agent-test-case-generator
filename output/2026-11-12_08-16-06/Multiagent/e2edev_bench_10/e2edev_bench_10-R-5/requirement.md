# e2edev\_bench\_10-R-5

After the user selects an option and clicks the <button> (data-testid: 'next-button') to proceed. Upon clicking, the system checks if an option is selected: if correct, it increments the score by 1; if not selected, it proceeds without scoring. The system updates to the next question or, if none remain, hides the question, options, and button (by adding the 'hidden' class) and displays the final score in the <div> (data-testid: 'score') with the message 'You scored {score} out of {total number of questions}'.
