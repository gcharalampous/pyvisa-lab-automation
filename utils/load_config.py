import yaml  # Import the PyYAML library for YAML file handling

def load_config(path):
    """
    Load a YAML configuration file from the given path.

    Args:
        path (str): The file path to the YAML config file.

    Returns:
        dict: The configuration loaded as a Python dictionary.
    """
    # Open the file at the specified path in read mode
    with open(path, 'r') as f:
        # Parse the YAML file and return the resulting dictionary
        return yaml.safe_load(f)
