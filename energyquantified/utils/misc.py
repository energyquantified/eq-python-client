

def dict_to_str(some_dict, prefix=""):
    """
    Converts a dict to a deterministic string for dicts that have the same
    keys and values (the string will be the same regardless of the original
    ordering of the keys).
    """
    keys_sorted = sorted(some_dict.keys())
    parts = [prefix]
    for k in keys_sorted:
        parts.append("|")
        parts.append(str(k))
        parts.append("=")
        parts.append(str(some_dict[k]))
    return "".join(parts)