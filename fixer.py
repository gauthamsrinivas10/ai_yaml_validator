def fix_config(template, config):
    """
    Fix config by ensuring it has all keys from template.
    For missing keys, copy from template.
    For lists, only fix first item.
    """
    if isinstance(template, dict) and isinstance(config, dict):
        fixed = {}
        for key in template:
            if key in config:
                fixed[key] = fix_config(template[key], config[key])
            else:
                fixed[key] = template[key]
        # Add any extra keys present in config (not in template)
        for key in config:
            if key not in fixed:
                fixed[key] = config[key]
        return fixed
    elif isinstance(template, list) and isinstance(config, list):
        if len(template) == 0:
            return config
        fixed_list = []
        if len(config) > 0:
            fixed_list.append(fix_config(template[0], config[0]))
            # Append remaining items as-is
            fixed_list.extend(config[1:])
        else:
            fixed_list = template
        return fixed_list
    else:
        # For primitives or type mismatch, prefer config's value
        return config
