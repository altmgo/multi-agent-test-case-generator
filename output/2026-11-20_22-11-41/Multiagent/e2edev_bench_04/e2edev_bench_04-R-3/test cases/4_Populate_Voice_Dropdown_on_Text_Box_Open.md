# Populate Voice Dropdown on Text Box Open

Case ID · G-004

Requirements · e2edev\_bench\_04-R-3

Preconditions: The text box is initially hidden. Steps: Click the 'Toggle Text Box' button (data-testid='toggle-button') to make the text box visible. Expected Behavior: The system invokes getVoices and populates the 'Choose Voice' dropdown (data-testid='voice-select') with option elements containing voice names and languages from the Web Speech API.
