import csv
import json

def read_csv_data(filepath,key):
    """Reads CSV file and extracts hidden conversations."""
    hidden_conversations = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            hidden_conversations.append(row[key])
    return hidden_conversations

def read_json_data(config_path,config_key):
    """Reads the configuration file."""
    with open(config_path, "r", encoding='utf-8') as f:
        data = json.load(f)
        prompt = [item[config_key] for item in data]
        return prompt

def read_json(config_path):
    """Reads the configuration file."""
    with open(config_path, "r", encoding='utf-8') as f:
        data = json.load(f)
        return data
    
def read_txt(filename):
    """Reads the content of a text file."""
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()