def normalize_language(original, choices):
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