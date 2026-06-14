import json
import os
from datetime import datetime

# Define a local file path to store the history data
HISTORY_FILE = "analysis_history.json"

def save_analysis_to_history(filename: str, score: int, grade: str) -> None:
    """
    Saves a snapshot of the code analysis (timestamp, filename, score, grade)
    to a local JSON file to keep track of student history.
    """
    # 1. Prepare the historical log entry
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename if filename else "Direct Input Text Area",
        "score": score,
        "grade": grade
    }

    # 2. Read existing history data if the file already exists
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # If the file is corrupted, reset it as an empty list
            history_data = []
    else:
        history_data = []

    # 3. Add the new run to the list and save it back to disk
    history_data.append(new_entry)
    
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)
    except IOError as e:
        print(f"Error saving history log locally: {e}")

def load_analysis_history() -> list:
    """
    Loads and returns the history log of previous code analysis runs.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

# Simple local tester
if __name__ == "__main__":
    print("Testing local history logging in utils.py...")
    save_analysis_to_history("test_script.py", 85, "B")
    current_history = load_analysis_history()
    print(f"Current logs found: {len(current_history)} entry/entries saved successfully.")