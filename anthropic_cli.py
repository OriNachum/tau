import argparse
import requests
import os
import datetime
from dotenv import load_dotenv
from modelproviders.anthropic_client import generate_response
from persistency.local_file import save_to_history, load_history

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("ANTHROPIC_API_KEY")
HISTORY_FILE = "conversation_history.txt"
SYSTEM_PROMPT_FILE = "prompts/system.md"

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

def load_prompt(name):
    system_prompt_file = f"./prompts/{name}/{name}.system.md"
    if os.path.exists(system_prompt_file):
        with open(system_prompt_file, "r") as file:
            return file.read()
    else:
        return ""

def get_time_since_last(history):
    # Get the last entry's timestamp from the history
    last_entry = history.strip().split("\n")[-1]
    if "[User]" in last_entry:
        last_timestamp_str = last_entry.split("[User]: ")[0]
    elif "[Assistant]" in last_entry:
        last_timestamp_str = last_entry.split("[Assistant]: ")[0]
    else:
        return None

    # Convert the timestamp string to a datetime object
    last_timestamp_obj = datetime.datetime.strptime(last_timestamp_str, "%Y-%m-%d %H:%M:%S")

    # Calculate the time since the last correspondence
    time_since_last = datetime.datetime.now() - last_timestamp_obj

    return time_since_last

if __name__ == "__main__":
    history = load_history()
    main_system_prompt = load_prompt("main")
    model_selector_system_prompt = load_prompt("model-selector")
    print("Conversation History:\n")
    print(history)

    # Request for a prompt
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = input("Please enter a prompt: ")
    if time_since_last:
        prompt = f"[{current_datetime}, {str(time_since_last).split('.')[0]}] {prompt}"
    else:
        prompt = f"[{current_datetime}] {prompt}"
        
    save_to_history("User", prompt)

    #response = generate_response(prompt, history, system_prompt, "haiku")
    response = generate_response(prompt, history, model_selector_system_prompt, "sonnet")
    print(f"Selected {response}")
    response = generate_response(prompt, history, main_system_prompt, response)
    print(response)
    save_to_history("Assistant", response)
