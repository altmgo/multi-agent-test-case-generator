# Opening Text Box When Web Speech API Returns Empty Voices

Case ID · G-040

Requirements · e2edev\_bench\_04-R-3

Trigger the opening of the text box via the toggle button when speechSynthesis.getVoices() returns an empty list or fails to load initially, ensuring the dropdown (data-testid='voice-select') handles the empty state gracefully and updates correctly upon a subsequent 'voiceschanged' event.
