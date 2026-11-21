# Update Voice Dropdown on Voices Changed Event

Case ID · G-005

Requirements · e2edev\_bench\_04-R-3

Preconditions: The text box is open and voices are initially loaded. Steps: Trigger the 'voiceschanged' event via the Web Speech API. Expected Behavior: The 'Choose Voice' dropdown (data-testid='voice-select') updates its option elements automatically to reflect the new list of available voices.
