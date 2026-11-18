# Abnormal Submission with Invalid Grade Outside 0-100 Range

Case ID · G-014

Requirements · e2edev\_bench\_49-R-1, e2edev\_bench\_49-R-2, e2edev\_bench\_49-R-5

Enter a student name and an invalid grade (e.g., -1 or 101) into 'student-grade' in the Student Grade Book interface, then click 'add-student-button'. Verify that the submission is prevented, an error message indicating the valid range is displayed, the student is not added to 'student-list', and the input fields retain their entered values.
