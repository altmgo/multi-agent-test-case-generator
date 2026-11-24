# Dropdown population failure when speech synthesis getVoices returns empty array initially

Case ID · G-126

Requirements · e2edev\_bench\_04-R-3

Verify the system handles cases where speechSynthesis.getVoices() returns an empty list upon opening the text box, ensuring it correctly falls back or listens for the 'voiceschanged' event without crashing.
