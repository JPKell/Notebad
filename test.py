import re

float_pattern = r'\b-?\d*\.\d+\b'
float_regex = re.compile(float_pattern)

# Test with example strings
test_strings = [
    "123.45",
    "-123.45",
    ".123",
    "-.123",
    "123",
    "abc",
]

for string in test_strings:
    match = float_regex.match(string)
    if match:
        print(f"{string}: Valid float")
    else:
        print(f"{string}: Invalid float")
