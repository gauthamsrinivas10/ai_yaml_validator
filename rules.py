def check_required_keys(template, actual, path=""):
    """
    Recursively check for required keys in the actual YAML config
    based on the template structure. Return a list of missing keys.
    """
    missing_keys = []

    if isinstance(template, dict):
        if not isinstance(actual, dict):
            missing_keys.append(path or "root (expected dict, got something else)")
            return missing_keys

        for key in template:
            new_path = f"{path}.{key}" if path else key
            if key not in actual:
                missing_keys.append(new_path)
            else:
                missing_keys.extend(
                    check_required_keys(template[key], actual[key], path=new_path)
                )

    elif isinstance(template, list) and isinstance(actual, list):
        for i in range(min(len(template), len(actual))):
            missing_keys.extend(
                check_required_keys(template[i], actual[i], path=f"{path}[{i}]")
            )

    return missing_keys
