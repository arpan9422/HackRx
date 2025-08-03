import json

def find_answer_from_map(question, json_file_path='mfile.json'):
    """
    Searches for a question in a JSON file and returns its corresponding answer.

    :param question: str, the question to search for
    :param json_file_path: str, path to the JSON file (default is 'mfile.json')
    :return: str or None, the answer if found, else None
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            question_map = json.load(f)
        
        # Normalize for matching if necessary (e.g., strip, lowercase)
        question = question.strip()

        # Exact match lookup
        return question_map.get(question, None)

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
        return None
    except json.JSONDecodeError:
        print("Error: JSON file is malformed.")
        return None
