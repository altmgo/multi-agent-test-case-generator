# Populate Voice Dropdown on Open

Case ID · G-003

Requirements · e2edev\_bench\_04-R-3

Preconditions: The text box is initially hidden. Steps: Click the toggle button (data-testid='toggle-button') to make the text box visible, and verify that the 'Choose Voice' dropdown (data-testid='voice-select') is populated with option elements representing available voices and languages retrieved via speechSynthesis.getVoices().
