import pytest

from src.trie_node import TrieNode


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty_name"),
        pytest.param("a", id="single_char_name"),
        pytest.param("file.txt", id="file_name_with_extension"),
        pytest.param("folder-name", id="name_with_hyphen"),
    ],
)
def test_trie_node_init(name):
    node = TrieNode(name)
    assert node.name == name
    assert node.children == {}
    assert node.is_file is False
    assert node.content == ""


def test_trie_node_children_are_independent_between_instances():
    # regression guard: children must be created per-instance, not shared/mutable-default state
    node_a = TrieNode("a")
    node_b = TrieNode("b")

    node_a.children["x"] = TrieNode("x")

    assert node_b.children == {}
