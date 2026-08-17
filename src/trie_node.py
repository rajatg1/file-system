class TrieNode:
    def __init__(self, name):
        self.name = name
        self.children = {}
        self.is_file = False
        self.content = ""
