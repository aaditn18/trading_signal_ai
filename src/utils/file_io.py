import yaml
import os
import json
from pathlib import Path

def load_yaml_config(config_path):
    """
    Load a YAML configuration file
    
    Args:
        config_path (str): Path to the YAML config file
        
    Returns:
        dict: Configuration as a dictionary
    """
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Error loading config file {config_path}: {str(e)}")
        
def save_json(data, file_path):
    """
    Save data as JSON to the specified file path
    
    Args:
        data (dict): Data to save
        file_path (str): Path to save the JSON file
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise Exception(f"Error saving JSON to {file_path}: {str(e)}")

def load_json(file_path):
    """
    Load JSON data from the specified file path
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Error loading JSON from {file_path}: {str(e)}")
