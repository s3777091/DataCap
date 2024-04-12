import json
import threading
from queue import Queue
import sys
import requests
from bs4 import BeautifulSoup
from tool import extract_code_by_id, extract_detection_methods, extract_text_by_priority


def generateUrls(start, end):
    return [f'https://cwe.mitre.org/data/definitions/{i}.html' for i in range(start, end + 1)]

def checkData(max_cwe):
    try:
        with open('data.json', 'r') as file:
            existing_data = json.load(file)
            existing_links = [item['url'] for item in existing_data]
            existing_numbers = [int(link.split('/')[-1].replace('.html', '')) for link in existing_links]
            if existing_numbers and max(existing_numbers) >= max_cwe:
                print(f"Data for CWEs up to {max_cwe} already exists in data.json.")
                return True
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return False

def fetchParse(url):
    for _ in range(2):  # Try twice
        try:
            response = requests.get(url)
            if response.status_code == 404:
                print(f"404 error for {url}, retrying...")
                continue  # Retry once if 404 encountered
            response.raise_for_status()  # Raises an HTTPError if the response was an error
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Request error: {e}")
    return None


skipped_urls = []


def process_url(url, queue):
    global skipped_urls  # Ensure the function can access the global list
    cwe_number = url.split('/')[-1].replace('.html', '')
    soup = fetchParse(url)
    if soup:
        title = soup.find('h2').text.strip() if soup.find('h2') else 'No title'
        description_or_summary = extract_text_by_priority(soup, cwe_number)
        examples = extract_code_by_id(soup, f'oc_{cwe_number}_Demonstrative_Examples')
        detection_methods = extract_detection_methods(soup, f'oc_{cwe_number}_Detection_Methods')

        if description_or_summary:
            data = {
                'title': title,
                'Description or Summary': description_or_summary,
                'url': url,
                'Examples': examples,
                'Detection Methods': detection_methods,
            }
            queue.put(data)
        else:
            # If the critical content is missing, consider the URL as skipped
            skipped_urls.append(url)
            print(f"Content missing, skipped {url}.")
    else:
        # Log or collect URLs that resulted in errors or missing content
        skipped_urls.append(url)
        print(f"Skipping {url} due to missing content or repeated 404 errors.")


def main(start, end):
    global skipped_urls
    if checkData(end):
        return

    links = generateUrls(start, end)
    queue = Queue()
    threads = []

    for url in links:
        thread = threading.Thread(target=process_url, args=(url, queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    with open('data.json', 'w') as file:
        json.dump(results, file, indent=4)

    # After processing, check if there are any skipped URLs
    if skipped_urls:
        print("The following URLs were skipped due to missing content or errors:")
        for url in skipped_urls:
            print(url)

    print(f"Data for CWEs {start}-{end} has been exported to data.json successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2 or '-' not in sys.argv[1]:
        print("Usage: python main.py <start>-<end>")
        sys.exit(1)

    start_end = sys.argv[1].split('-')
    start, end = int(start_end[0]), int(start_end[1])
    main(start, end)
