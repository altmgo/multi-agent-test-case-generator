# e2edev\_bench\_26-R-5

The web application must provide a '替换' (Replace) functionality that allows users to replace occurrences of specified text within a paragraph. The functionality should adhere to the following requirements: 

1. **UI Elements and Interactions:**
   - The '替换' functionality is accessible via a dropdown menu triggered by clicking the '展开' list item with `data-testid='expand-list-item'`.
   - Within the dropdown, the user must click the '替换' list item with `data-testid='replace-list-item'` to display the '替换' tab with `data-testid='replace`.
   - The '替换' tab contains:
     - An input field for the old text with `data-testid='replace-input-old'`.
     - An input field for the new text with `data-testid='replace-input-new'`.
     - A button labeled '替换' with `data-testid='replace-button'`.

2. **Functionality:**
   - When the user enters text into both input fields and clicks the '替换' button:
     - All occurrences of the old text (case-sensitive) in the paragraph should be replaced with the new text.
     - The paragraph should visually highlight the replaced text using a `<span>` element with a yellow background.
   - If the old text appears multiple times in the paragraph, all occurrences must be replaced.
   - If the old text is a substring of other words, only the exact matches should be replaced.

3. **Error Handling:**
   - If the old text is not found in the paragraph, an alert should be displayed with the message '未找到您要找的文字！'.
   - If the old text input field is empty, an alert should be displayed with the message '请输入文字！'.

4. **Expected Results:**
   - The paragraph's content should be updated dynamically in the DOM to reflect the replacements.
   - The original paragraph content should be restored when switching between tabs or dropdown options.

5. **Boundary Conditions:**
   - The system must handle edge cases where the old text appears multiple times or is a substring of other words.
   - The system must ensure that the replacement process does not affect unrelated text or introduce formatting errors.

6. **UI Behavior:**
   - The '替换' tab should only be displayed when the corresponding dropdown option is selected.
   - The dropdown menu should toggle visibility when the '展开' list item is clicked.

This refined requirement ensures that the '替换' functionality is robust, user-friendly, and handles all specified scenarios, including normal cases, edge cases, and error conditions.
