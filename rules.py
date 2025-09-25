def check_required_keys(template, actual, path="root."):
    """
    Recursively check if keys in template exist in actual.
    Returns list of missing keys as strings.
    """
    missing = []

    if isinstance(template, dict):
        if not isinstance(actual, dict):
            missing.append(path.rstrip('.'))
            return missing

        for key in template:
            if key not in actual:
                missing.append(path + str(key))
            else:
                missing.extend(check_required_keys(template[key], actual[key], path + str(key) + "."))

    elif isinstance(template, list):
        if not isinstance(actual, list):
            missing.append(path.rstrip('.'))
            return missing

        for i, item in enumerate(template):
            # Check only first item of list to avoid excessive recursion
            if i == 0 and len(actual) > 0:
                missing.extend(check_required_keys(item, actual[0], path + f"[{i}]."))
    return missing
