# Filesystem Programming Problem

## Problem

Design and implement an **in-memory filesystem**.

The filesystem should support basic operations for creating directories, creating/updating files, reading files, and listing directory contents.

### APIs

Implement the following operations:

```text
mkdir(path)
addContentToFile(filePath, content)
readContentFromFile(filePath)
ls(path)
```

## Solution

### Design

The filesystem is modeled as a **trie**, where each path segment (the string between `/` characters) is a node, and the path from the root to a node represents the full path to a file or directory.

- **`TrieNode`** (`src/trie_node.py`) — a single node in the tree.
  - `name`: the path segment this node represents.
  - `children`: `dict` mapping child segment names to child `TrieNode`s.
  - `is_file`: `bool` flag distinguishing files from directories.
  - `content`: `str` file content (empty/unused for directories).
- **`Trie`** (`src/trie.py`) — the underlying tree structure with two primitives:
  - `addWord(path, is_file=False, content="")`: walks the given list of path segments from the root, creating any missing intermediate nodes, and returns the terminal node. If `is_file=True`, marks the terminal node as a file and **appends** `content` to it.
  - `search(path)`: walks the given list of path segments and returns the terminal node, or `None` if any segment doesn't exist.
- **`FileSystem`** (`src/filesystem.py`) — the public API, backed by a `Trie` instance.
  - `_parse_path(path)`: shared helper that validates a path string and splits it into a list of segments (or returns `None` if invalid). Used by every public method.
  - `mkdir(path)`, `addContentToFile(filePath, content)`, `readContentFromFile(filePath)`, `ls(path)`: implemented on top of `_parse_path` plus `Trie.addWord` / `Trie.search`.

### Path validation rules

A path is valid if:
- It is the empty string `""`, which represents the root directory, **or**
- It starts with `/`, and every segment between slashes is non-empty and has no leading/trailing whitespace.

Examples of invalid paths: `"/a/b/c///d"` (consecutive slashes), `"/a/b/     f/g"` (whitespace in a segment), `"ab/c/"` (missing leading slash), `"/a/b/"` (trailing slash), `"/"` (empty segment after the leading slash).

### API behavior

- **`mkdir(path)`** — creates all missing directories along `path`. Returns `True` on success, `False` for an invalid path. Calling it on an existing path is idempotent (returns `True`, no changes made).
- **`addContentToFile(filePath, content)`** — creates any missing parent directories and the file itself if needed, then **appends** `content` to the file (repeated calls accumulate content rather than overwrite it). Returns `True` on success, `False` for an invalid path.
- **`readContentFromFile(filePath)`** — returns the file's content as a string. Returns `None` if the path is invalid, doesn't exist, or refers to a directory.
- **`ls(path)`** — returns a sorted list of the names of the entries directly inside a directory, or a single-element list `[name]` if `path` points to a file. Returns `None` if the path is invalid or doesn't exist. `ls("")` lists the top-level (root) entries.

### Project structure

```text
src/
  filesystem.py    # FileSystem: public API
  trie.py          # Trie: addWord / search primitives
  trie_node.py     # TrieNode: children, is_file, content
tests/
  test_filesystem.py
  test_trie.py
  test_trie_node.py
```

### Running tests

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python3 -m pytest -v
```

Run the test suite with a coverage report:

```bash
python3 -m pytest --cov=src --cov-report=term-missing
```
