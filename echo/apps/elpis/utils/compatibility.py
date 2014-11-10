def normalize_language(original, choices):
    """
    Matches original language to an appropriate selection from a list of languages.

    For example, if 'english' is the original language and 'en-us' is in choices, normalize_language
    will return 'en-us'. If the original language is already present in choices, it will be returned
    unmodified.
    """
    if original in choices:
        return original
    elif original == 'english' and 'en-us' in choices:
        return 'en-us'
    elif original == 'spanish' and 'es-us' in choices:
        return 'es-us'
    elif original == 'en-us' and 'english' in choices:
        return 'english'
    elif original == 'es-us' and 'spanish' in choices:
        return 'spanish'
    else:
        return False