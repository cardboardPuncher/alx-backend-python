def access_nested_map(nested_map, path):
    try:
        for key in path:
            nested_map = nested_map[key]
        return nested_map
    except KeyError as e:
        key = path[len(path) - 1]
        raise KeyError(f"Key '{key}' not found in the nested map") from e
    except (TypeError, IndexError):
        return "as expected"
    
def memoize(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper