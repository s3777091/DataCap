import json


def transfer_data(old_file_path, new_file_path):
    # Read the old JSON file
    with open(old_file_path, 'r') as file:
        old_data = json.load(file)

    # Check if old_data is a list and process accordingly
    if isinstance(old_data, list):
        # Create a new data structure for each entry
        new_data_list = []
        for entry in old_data:
            new_data = {
                "instruction": entry["problem"],
                "output": entry["answer"][0]["content"]
            }
            new_data_list.append(new_data)

        # Write the new JSON file with a list of new entries
        with open(new_file_path, 'w') as file:
            json.dump(new_data_list, file, indent=4)
    else:
        # Single entry processing (original function behavior)
        new_data = {
            "instruction": old_data["problem"],
            "output": old_data["answer"][0]["content"]
        }
        # Write the new JSON file
        with open(new_file_path, 'w') as file:
            json.dump(new_data, file, indent=4)


# Example usage:
transfer_data('./Exploit/output/results.json', './Exploit/output/results2.json')
