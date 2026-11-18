# e2edev\_bench\_20-R-3

When the user interacts with the 'Register a Car' form in the 'Car Registration System' web application, the following requirements must be met: 
1. The form must include the following fields with their respective attributes: 
   - 'Owner's Name' field, located by data-testid 'owner-name-input', which accepts text input. 
   - 'Car Model' field, located by data-testid 'car-model-input', which accepts text input. 
   - 'License Number' field, located by data-testid 'license-number-input', which accepts text input. 
   - 'Registration Date' date picker field, located by data-testid 'registration-date-input', which accepts a date input or select. 
2. When the user clicks the 'Save Registration' button, located by data-testid 'submit-button', the system must validate that all fields are filled. 
3. The following scenarios must be handled: 
   - If all fields are filled: 
     - The system must save the registration data in localStorage under the key 'registrations'. 
     - The registration data must include the following properties: 'ownerName', 'carModel', 'licenseNumber', and 'registrationDate'. 
     - The saved registration must be displayed in the 'All Registrations' table, located by data-testid 'registration-table', with each property displayed in its respective column. 
     - The form must be reset, clearing all input fields. 
   - If any field is empty: 
     - The system must display an alert with the message 'Please fill out all fields.' 
The system must ensure that the 'Save Registration' button is functional only when the 'Register a Car' tab is active, as determined by the presence of the 'active' class on the tab button located by data-testid 'register-tab-button'.
