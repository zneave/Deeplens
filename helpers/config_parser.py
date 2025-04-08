import yaml

def load_ui_config(filepath):
    """
    Loads the UI configuration from a YAML file.
    """
    with open(filepath, "r") as file:
        config = yaml.safe_load(file)
    return config
