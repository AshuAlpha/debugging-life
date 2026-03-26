import json
import os
import sys
from datetime import datetime

TASK_FILE = 'tasks.json'
VALID_STATUS = {"TODO", "IN_PROGRESS", "DONE"}

def now_iso():
    return datetime.now().isoformat(timespec='seconds')

def ensure_task_file():
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'w',encoding="utf-8") as f:
            json.dump([], f)
            
def load_tasks():
    ensure_task_file()
    try:
        with open(TASK_FILE, 'r',encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Error: {TASK_FILE} is invalid. Expected a list of tasks.")
                sys.exit(1)
            return data
    except json.JSONDecodeError:
        print(f"Error: {TASK_FILE} is not a valid JSON file.")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading {TASK_FILE}: {e}")
        sys.exit(1)
        
#! 
        
def save_tasks(tasks):
    try:
        with open(TASK_FILE, 'w', encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        print(f"Error writing to {TASK_FILE}: {e}")
        sys.exit(1)
        
def next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

def parse_task_id(raw): # Parses a raw string input into a valid task ID (positive integer). Helps ensure that the input is valid and provides error handling for invalid cases.
    try:
        task_id= int(raw)
        if task_id <= 0:
            raise ValueError
        return task_id
    except ValueError:
        print("Error: Task ID must be a positive integer.")
        sys.exit(1)
        
def add_task(description):
    description = description.strip()
    if not description:
        print("Error: Task description cannot be empty.")
        sys.exit(1)
    
    tasks = load_tasks()
    new_task = {
        'id': next_id(tasks),
        'description': description,
        'status': 'TODO',
        'created_at': now_iso(),
        'updated_at': now_iso()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task added with ID {new_task['id']}.") 
    
def update_task(task_id, description):
    description = description.strip()
    if not description:
        print("Error: Task description cannot be empty.")
        sys.exit(1)
    
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if task is None:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)
    
    task['description'] = description
    task['updated_at'] = now_iso()
    save_tasks(tasks)
    print(f"Task {task_id} updated successfully.")
    
def delete_task(task_id):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if task is None:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)
    
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print(f"Task {task_id} deleted successfully.")
    
def mark_task(task_id, status):
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    if task is None:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)
    
    task['status'] = status
    task['updated_at'] = now_iso()
    save_tasks(tasks)
    print(f"Task {task_id} marked as {status}.")
    
def list_tasks(filter_status = None):
    tasks = load_tasks()
    
    if filter_status is not None:
        if filter_status not in VALID_STATUS:
            print(f"Error: Invalid status '{filter_status}'. Valid statuses are: {', '.join(VALID_STATUS)}.")
            sys.exit(1)
        tasks = [t for t in tasks if t['status'] == filter_status]
        
    if not tasks:
        print("No tasks found.")
        return
    
    for task in tasks:
        print(
            f"[{task['id']}] {task['description']} |"
            f"(Status: {task['status']} |"
            f" Created: {task['created_at']} |"
            f"Updated: {task['updated_at']}) "
        )
    
def print_help():
    print(
        "Usage:\n"
        "  python Task_Tracker.py add \"Task description\" - Add a new task\n"
        "  python Task_Tracker.py update <task_id> \"New description\" - Update an existing task\n"
        "  python Task_Tracker.py delete <task_id> - Delete a task\n"
        "  python Task_Tracker.py mark <task_id> <status> - Mark a task with a status (TODO, IN_PROGRESS, DONE)\n"
        "  python Task_Tracker.py list [status] - List all tasks, optionally filtered by status\n"
        "  python Task_Tracker.py help - Show this help message"   
    )
    
def main():
    args = sys.argv[1:]
    
    if not args:
        print_help()
        sys.exit(0)
        
    command = args[0].lower()
    
    if command == "add":
        if len(args) != 2:
            print("Error: 'add' command requires a task description.")
            sys.exit(1)
        add_task(args[1])
    elif command == "update":
        if len(args) != 3:
            print("Error: 'update' command requires a task ID and a new description.")
            sys.exit(1)
        task_id = parse_task_id(args[1])
        update_task(task_id, args[2])
    elif command == "delete":
        if len(args) != 2:
            print("Error: 'delete' command requires a task ID.")
            sys.exit(1)
        task_id = parse_task_id(args[1])
        delete_task(task_id)
        
    elif command == "mark-in-progress":
        if len(args) != 2:
            print("Error: 'mark-in-progress' command requires a task ID.")
            sys.exit(1)
        task_id = parse_task_id(args[1])
        mark_task(task_id, "IN_PROGRESS")
    elif command == "mark-done":
        if len(args) != 2:
            print("Error: 'mark-done' command requires a task ID.")
            sys.exit(1)
        task_id = parse_task_id(args[1])
        mark_task(task_id, "DONE")
    elif command == "list":
        if len(args) > 2:
            print("Error: 'list' command takes at most one optional status filter.")
            sys.exit(1)
        filter_status = args[1] if len(args) == 2 else None
        list_tasks(filter_status)
    elif command == "help":
        print_help()
    else:
        print(f"Error: Unknown command '{command}'.")
        print_help()
        sys.exit(1)
if __name__ == "__main__":
    main()
