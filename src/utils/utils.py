def URLjoin(*args):
    """
    Join parts of a URL ensuring correct slashes.
    Kept as CamelCase URLjoin for compatibility, or updated to snake_case if references are updated.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))
