import yaml

def load_yaml_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"❌ Error loading YAML file {filepath}: {e}")
        return None

def write_yaml_file(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
    except Exception as e:
        print(f"❌ Error writing YAML file {filepath}: {e}")
