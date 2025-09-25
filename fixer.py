def auto_fix(template, actual):
    """
    Recursively add missing keys from the template to the actual config.
    """
    if isinstance(template, dict):
        if not isinstance(actual, dict):
            return template
        for key in template:
            if key not in actual:
                actual[key] = template[key]
            else:
                actual[key] = auto_fix(template[key], actual[key])
    elif isinstance(template, list):
        if not isinstance(actual, list):
            return template
        for i in range(min(len(template), len(actual))):
            actual[i] = auto_fix(template[i], actual[i])
    return actual
