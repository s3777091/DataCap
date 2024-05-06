import os
import re

# Define the directory and file name
directory = 'tab'
file_name = 'all_java_files.txt'  # Change this to the name of your Java file

# Full path to the Java file
file_path = os.path.join(directory, file_name)

class_pattern = r"public class (\w+)(?: extends (\w+))?\s*\{"
subclass_pattern = r"public static class (\w+)(?: extends (\w+))?\s*\{"
method_pattern = r"(public|private) \w+ (\w+)\(.*?\)\s*\{"

# Read the content of the Java file
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()
except FileNotFoundError:
    print(f"Error: File not found - {file_path}")
    java_code = ""

# Function to extract methods considering nested braces
def extract_methods(content):
    methods = []
    matches = list(re.finditer(method_pattern, content))
    for match in matches:
        start = match.end()
        braces = 1
        end = start
        while end < len(content) and braces > 0:
            if content[end] == '{':
                braces += 1
            elif content[end] == '}':
                braces -= 1
            end += 1
        methods.append((match.group(2), content[match.start():end]))  # Capture method name
    return methods

# Function to identify class usages within another class content
def find_class_usages(class_name, content, other_classes):
    usages = set()
    for other_class in other_classes:
        if other_class != class_name and re.search(r'\b' + re.escape(other_class) + r'\b', content):
            usages.add(other_class)
    return list(usages)

# Extract class blocks and details
class_blocks = [(m.group(1), m.start(), m.end()) for m in re.finditer(class_pattern, java_code)]
class_names = [cls[0] for cls in class_blocks]  # List of class names for reference
class_methods = {}
subclasses = {}

for cls, start_index, end_index in class_blocks:
    class_content = java_code[end_index:]
    open_braces = 1
    i = 0
    while open_braces > 0 and (i + end_index) < len(java_code):
        if class_content[i] == '{':
            open_braces += 1
        elif class_content[i] == '}':
            open_braces -= 1
        i += 1
    class_content = java_code[end_index:end_index + i]

    methods = extract_methods(class_content)
    usages = find_class_usages(cls, class_content, class_names)
    class_methods[cls] = {'methods': [m[0] for m in methods], 'parent': None, 'subclasses': [], 'usages': usages}

    # Processing subclasses similarly
    found_subclasses = [(m.group(1), m.group(2), m.start(), m.end()) for m in re.finditer(subclass_pattern, class_content)]
    for subcls, subparent, sub_start, sub_end in found_subclasses:
        sub_content = class_content[sub_end:]
        open_braces = 1
        j = 0
        while open_braces > 0 and (j + sub_end) < len(class_content):
            if sub_content[j] == '{':
                open_braces += 1
            elif sub_content[j] == '}':
                open_braces -= 1
            j += 1
        sub_content = class_content[sub_end:sub_end + j]
        sub_methods = extract_methods(sub_content)
        sub_usages = find_class_usages(subcls, sub_content, class_names)
        subclasses[subcls] = {'methods': [m[0] for m in sub_methods], 'parent': subparent, 'usages': sub_usages}
        class_methods[cls]['subclasses'].append(subcls)

for cls, details in class_methods.items():
    print(f"Class: {cls} (Extends {details['parent'] if details['parent'] else 'None'})")
    for method in details['methods']:
        print(f"  Method: {method}")
    if details['usages']:
        print(f"  Usages: {', '.join(details['usages'])}")

    for subcls in details['subclasses']:
        sub_details = subclasses[subcls]
        print(f"  Subclass: {subcls} (Extends {sub_details['parent']})")
        for method in sub_details['methods']:
            print(f"    Method: {method}")
        if sub_details['usages']:
            print(f"    Usages: {', '.join(sub_details['usages'])}")