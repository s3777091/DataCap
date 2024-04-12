from bs4 import BeautifulSoup


def extract_text_by_priority(soup, base_id, exclude_class=None):
    # Correctly construct ID patterns for extended description, description, and summary.
    section_ids = [
        f'oc_{base_id}_Extended_Description',
        f'oc_{base_id}_Description',
        f'oc_{base_id}_Summary'
    ]

    for section_id in section_ids:
        target_div = soup.find('div', id=section_id)
        if not target_div:
            continue

        # Check for 'indent' divs first.
        indent_div = target_div.find('div', class_='indent')
        if indent_div:
            return indent_div.get_text(strip=True)

        # If no 'indent' div found, fetch text directly from paragraphs, applying any class exclusions.
        paragraphs = target_div.find_all('p', class_=lambda x: x != exclude_class if exclude_class else True)
        if paragraphs:
            return '\n'.join(p.text.strip() for p in paragraphs).strip()

        # For cases without 'indent' or 'p' tags, return text from any child elements.
        # This includes direct text within the div or nested within other tags.
        return ' '.join(target_div.stripped_strings)

    # Return an empty string if none of the sections are found, indicating no relevant content.
    return ''

def clean_code(code_html):
    return "\n".join(string for string in code_html.stripped_strings if not string.startswith("//"))

def extract_code_by_id(url, section_id):
    target_div = url.find('div', id=section_id)
    examples = []
    if target_div:
        for subheading in target_div.find_all('p', class_='subheading'):
            description = "\n".join(sibling.text.strip() for sibling in subheading.find_all_next('p', class_=False))
            code_div = subheading.find_next('div', class_='shadow')
            code = clean_code(code_div) if code_div else 'No code'
            examples.append({'description': description, 'code': code})
    return examples

def extract_detection_methods(url, section_id):
    methods = []
    target_div = url.find('div', id=section_id)
    if not target_div:
        return methods

    for row in target_div.find_all('tr'):
        subheading = row.find('p', class_='subheading')
        if subheading:
            name = subheading.text.strip()
            descriptions = [desc.get_text(" ", strip=True) for desc in row.find_all('div', class_='indent') if
                            desc.text.strip()]
            description = ' '.join(descriptions)
            methods.append({'name': name, 'description': description})

    return methods
