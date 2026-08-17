import pytest

from src.trie import Trie
from src.trie_node import TrieNode


@pytest.fixture
def trie():
    return Trie()


def _run(obj, setup):
    """Run a list of (method_name, args, kwargs) calls against obj before the real assertion."""
    for entry in setup:
        method_name, args = entry[0], entry[1]
        kwargs = entry[2] if len(entry) > 2 else {}
        getattr(obj, method_name)(*args, **kwargs)


def test_trie_init_creates_empty_root(trie):
    assert isinstance(trie.root, TrieNode)
    assert trie.root.name == ""
    assert trie.root.children == {}
    assert trie.root.is_file is False
    assert trie.root.content == ""


@pytest.mark.parametrize(
    "setup, path, kwargs, expected_name, verify",
    [
        # happy path
        pytest.param([], [], {}, "", lambda trie, node: trie.root is node, id="empty_path_returns_root"),
        pytest.param(
            [], ["a"], {}, "a", lambda trie, node: trie.root.children["a"] is node, id="single_level_creates_child"
        ),
        pytest.param(
            [],
            ["a", "b", "c"],
            {},
            "c",
            lambda trie, node: trie.root.children["a"].children["b"].children["c"] is node,
            id="nested_path_creates_intermediate_nodes",
        ),
        pytest.param(
            [], ["a"], {}, "a", lambda trie, node: node.is_file is False and node.content == "", id="default_is_not_file"
        ),
        pytest.param(
            [],
            ["a"],
            {"is_file": True, "content": "hello"},
            "a",
            lambda trie, node: node.is_file is True and node.content == "hello",
            id="is_file_true_sets_content",
        ),
        # append / idempotency behavior
        pytest.param(
            [("addWord", (["a"],), {"is_file": True, "content": "hello"})],
            ["a"],
            {"is_file": True, "content": " world"},
            "a",
            lambda trie, node: node.content == "hello world",
            id="repeated_calls_append_content",
        ),
        pytest.param(
            [("addWord", (["a"],), {})],
            ["a"],
            {},
            "a",
            lambda trie, node: trie.root.children["a"] is node,
            id="duplicate_path_reuses_existing_node",
        ),
        pytest.param(
            [("addWord", (["a", "b"],), {}), ("addWord", (["a", "c"],), {})],
            ["a", "d"],
            {},
            "d",
            lambda trie, node: set(trie.root.children["a"].children.keys()) == {"b", "c", "d"},
            id="branching_paths_do_not_disturb_siblings",
        ),
    ],
)
def test_add_word(trie, setup, path, kwargs, expected_name, verify):
    _run(trie, setup)
    node = trie.addWord(path, **kwargs)
    assert node.name == expected_name
    assert verify(trie, node)


@pytest.mark.parametrize(
    "setup, path, expected",
    [
        # happy path
        pytest.param([], [], "root", id="empty_path_returns_root"),
        pytest.param([("addWord", (["a"],), {})], ["a"], "node", id="existing_single_level_path"),
        pytest.param([("addWord", (["a", "b", "c"],), {})], ["a", "b", "c"], "node", id="existing_nested_path"),
        # sad path
        pytest.param([], ["missing"], None, id="nonexistent_top_level_segment"),
        pytest.param([("addWord", (["a"],), {})], ["a", "b"], None, id="valid_prefix_invalid_child"),
    ],
)
def test_search(trie, setup, path, expected):
    _run(trie, setup)
    result = trie.search(path)

    if expected is None:
        assert result is None
    elif expected == "root":
        assert result is trie.root
    else:  # "node" -> verify identity against a direct manual traversal
        node = trie.root
        for part in path:
            node = node.children[part]
        assert result is node
