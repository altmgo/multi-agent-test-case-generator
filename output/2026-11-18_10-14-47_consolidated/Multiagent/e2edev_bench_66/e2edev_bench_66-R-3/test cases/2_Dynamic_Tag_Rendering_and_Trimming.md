# Dynamic Tag Rendering and Trimming

Case ID · G-002

Requirements · e2edev\_bench\_66-R-1, e2edev\_bench\_66-R-2, e2edev\_bench\_66-R-3

Verify that comma-separated inputs entered into the textarea are dynamically parsed, leading/trailing spaces are trimmed, empty entries are ignored, and valid choices are rendered as span elements with class 'tag' and unique 'tag-{index}' data-id attributes inside data-testid='tags-container'.
