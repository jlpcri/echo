class DirectoryTree(object):
    """
    Creates a nested list representing a Linux directory structure.

    Example usage:
    dt = DirectoryTree()
    dt.add('/path/to/some/file.wav')
    dt.add('/path/to/some/other.wav')
    dt.add('/path/to/another/place.wav')
    dt.entries

    To exclude a common root path:
    dt = DirectoryTree('/path/to/')
    dt.add('/path/to/some/file.wav')
    dt.add('/path/to/some/other.wav')
    dt.add('/path/to/another/place.wav')
    dt.entries
    """
    def __init__(self, path=""):
        self.path = path
        self.entries = []

    def _path_to_components(self, filepath):
        """Strips root path and returns list of directories"""
        if self.path:
            if not filepath.startswith(self.path):
                raise FileNotOnPathError('{0} is not on path {1}'.format(filepath, self.path))
            scoped_filepath = filepath[len(self.path):]
            return scoped_filepath.split('/')
        else:
            return filepath.split('/')

    def add(self, filepath):
        """Adds a new file to entries"""
        components = self._path_to_components(filepath)
        search_scope = self.entries
        for i, component in enumerate(components):
            try:
                j = search_scope.index(component + ('/' if i+1 != len(components)
                                                    else ''))
                search_scope = search_scope[j+1]
            except ValueError:
                if i+1 != len(components):
                    search_scope.extend([component+'/', []])
                    search_scope = search_scope[-1]
                else:
                    search_scope.extend([component])
            except IndexError as e:
                if i+1 == len(components):
                    pass
                else:
                    raise e

    def __contains__(self, filepath):
        """
        'if filepath in DirectoryTree' functionality

        Returns False for anything except a full path to a file. For example,
        '/path/to/this/file.txt' does not make '/path/to/' in DirectoryTree
        True.
        """
        components = self._path_to_components(filepath)
        search_scope = self.entries
        for i, component in enumerate(components):
            try:
                j = search_scope.index(component + ('/' if i+1 != len(components)
                                                    else ''))
                search_scope = search_scope[j+1]
            except ValueError:
                    return False
            except IndexError as e:
                if i+1 == len(components):
                    return True
                else:
                    raise e
        raise RuntimeError("Unexpectedly ended search loop")


class FileNotOnPathError(Exception):
    """Raised when file added does not include the file root"""
    pass


class DirectoryTreeWithPayload(DirectoryTree):
    """A DirectoryTree that associates child nodes with a class"""

    class PayloadObject(object):
        def __init__(self, name, payload):
            self.name = name
            self.payload = payload

    def __init__(self, path='', payload_class=None):
        if not payload_class:
            raise SyntaxError('payload_class is a required argument')
        self.path = path
        self.entries = []
        self.file_list = []
        self.payload_class = payload_class

    def add(self, filepath, init=()):
        components = self._path_to_components(filepath)
        search_scope = self.entries
        for i, component in enumerate(components):
            try:
                j = search_scope.index(component + ('/' if i+1 != len(components)
                                                    else ''))
                search_scope = search_scope[j+1]
            except ValueError:
                if i+1 != len(components):
                    search_scope.extend([component+'/', []])
                    search_scope = search_scope[-1]
                else:
                    for entry in search_scope:
                        if entry.name == component:
                            search_scope.remove(entry)
                    search_scope.append(self.PayloadObject(component, self.payload_class(*init)))
            except IndexError as e:
                if i+1 == len(components):
                    pass
                else:
                    raise e
        self.file_list.append(self.PayloadObject(filepath, self.payload_class(*init)))

    def __contains__(self, filepath):
        return (filepath in [entry.name for entry in self.file_list])

    def __iter__(self):
        return self.file_list.__iter__()

    def __getitem__(self, key):
        """Return payload class object for given filepath"""
        for f in self.file_list:
            if f.name == key:
                return f.payload
        return None

    def __setitem__(self, key, value):
        if key not in self:
            super.add(key)
            self.file_list.append(self.PayloadObject(key, value))
        else:
            for f in self.file_list:
                if f.name == key:
                    f.payload = value



