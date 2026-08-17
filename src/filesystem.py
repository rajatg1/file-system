from src.trie import Trie


class FileSystem:
    def __init__(self):
        self.trie = Trie()

    def _parse_path(self, path):
        """Validate path and split it into components.

        Returns the list of path components if the path is valid,
        or None if the path is invalid.
        """
        if path == "":
            return []

        if not path.startswith("/"):
            return None

        parts = path.split("/")[1:]

        for part in parts:
            if part == "" or part != part.strip():
                return None

        return parts

    def mkdir(self, path):
        parts = self._parse_path(path)
        if parts is None:
            return False

        self.trie.addWord(parts)
        return True

    def addContentToFile(self, filePath, content):
        parts = self._parse_path(filePath)
        if parts is None:
            return False

        self.trie.addWord(parts, is_file=True, content=content)
        return True

    def readContentFromFile(self, filePath):
        parts = self._parse_path(filePath)
        if parts is None:
            return None

        node = self.trie.search(parts)
        if node is None or not node.is_file:
            return None

        return node.content

    def ls(self, path):
        parts = self._parse_path(path)
        if parts is None:
            return None

        node = self.trie.search(parts)
        if node is None:
            return None

        if node.is_file:
            return [node.name]

        return sorted(node.children.keys())
