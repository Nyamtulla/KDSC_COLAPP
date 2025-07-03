import re

# Test the specific line from the Walmart receipt
line = "Su HRO FGHTR 06305094073 6.94 T"

# Pattern 9 from our OCR script
pattern = re.compile(r'^([A-Z\s]+)\s+(\d{11,12})\s+(\d+\.\d{2})\s+[A-Z]$')

print(f"Testing line: '{line}'")
print(f"Pattern: {pattern.pattern}")

match = pattern.match(line)
print(f"Match result: {match}")

if match:
    print(f"Groups: {match.groups()}")
    print(f"Group 1 (product): '{match.group(1)}'")
    print(f"Group 2 (barcode): '{match.group(2)}'")
    print(f"Group 3 (price): '{match.group(3)}'")
else:
    print("No match!")
    
    # Let's try to see what's wrong
    print("\nDebugging:")
    print(f"Line starts with uppercase: {line[0].isupper()}")
    print(f"Line length: {len(line)}")
    barcode_match = re.search(r'\d{11,12}', line)
    price_match = re.search(r'\d+\.\d{2}', line)
    print(f"Contains barcode pattern: {bool(barcode_match)}")
    print(f"Contains price pattern: {bool(price_match)}")
    print(f"Ends with letter: {line[-1].isalpha()}")
    
    # Try a more flexible pattern
    flexible_pattern = re.compile(r'^(.+?)\s+(\d{11,12})\s+(\d+\.\d{2})\s+[A-Z]$')
    flexible_match = flexible_pattern.match(line)
    print(f"\nFlexible pattern match: {flexible_match}")
    if flexible_match:
        print(f"Flexible groups: {flexible_match.groups()}") 