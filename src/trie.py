from src.trie_node import TrieNode


class Trie:
    def __init__(self):
        self.root = TrieNode("")

    def addWord(self, path, is_file=False, content=""):
        current = self.root
        for part in path:
            if part not in current.children:
                current.children[part] = TrieNode(part)
            current = current.children[part]

        if is_file:
            current.is_file = True
            current.content += content

        return current

    def search(self, path):
        current = self.root
        for part in path:
            if part not in current.children:
                return None
            current = current.children[part]
        return current
