import pytest

from src.filesystem import FileSystem


@pytest.fixture
def fs():
    return FileSystem()


def _run(fs, setup):
    """Run a list of (method_name, args) calls against fs before the real assertion."""
    for method_name, args in setup:
        getattr(fs, method_name)(*args)


@pytest.mark.parametrize(
    "setup, path, expected, verify",
    [
        # happy path
        pytest.param([], "/a", True, None, id="simple_dir"),
        pytest.param([], "/a/b/c", True, lambda fs: fs.ls("/a/b") == ["c"], id="nested_dirs_created"),
        pytest.param([], "", True, None, id="empty_string_is_root"),
        # duplicate / idempotency
        pytest.param(
            [("mkdir", ("/a/b",))], "/a/b", True, lambda fs: fs.ls("/a") == ["b"], id="duplicate_is_idempotent"
        ),
        pytest.param(
            [("mkdir", ("/a/b",)), ("mkdir", ("/a/c",))],
            "/a/d",
            True,
            lambda fs: fs.ls("/a") == ["b", "c", "d"],
            id="siblings_not_disturbed",
        ),
        # sad path / invalid paths
        pytest.param([], "/a/b/c///d", False, None, id="consecutive_slashes"),
        pytest.param([], "/a/b/     f/g", False, None, id="whitespace_in_segment"),
        pytest.param([], "ab/c/", False, None, id="missing_leading_slash"),
        pytest.param([], "/", False, None, id="root_slash_trailing_empty_segment"),
        pytest.param([], "/a/b/", False, None, id="trailing_slash"),
        pytest.param([], "//a", False, None, id="leading_double_slash"),
    ],
)
def test_mkdir(fs, setup, path, expected, verify):
    _run(fs, setup)
    assert fs.mkdir(path) is expected
    if verify is not None:
        assert verify(fs)


@pytest.mark.parametrize(
    "setup, file_path, content, expected, verify",
    [
        # happy path
        pytest.param([], "/a/file.txt", "hello", True, lambda fs: fs.readContentFromFile("/a/file.txt") == "hello", id="simple_file"),
        pytest.param([], "/a/b/c/file.txt", "data", True, lambda fs: fs.ls("/a/b") == ["c"], id="creates_missing_parents"),
        pytest.param([], "/file.txt", "", True, lambda fs: fs.readContentFromFile("/file.txt") == "", id="empty_content_allowed"),
        # append behavior
        pytest.param(
            [("addContentToFile", ("/file.txt", "hello"))],
            "/file.txt",
            " world",
            True,
            lambda fs: fs.readContentFromFile("/file.txt") == "hello world",
            id="repeated_calls_append",
        ),
        pytest.param(
            [("addContentToFile", ("/file.txt", "hello"))],
            "/file.txt",
            "",
            True,
            lambda fs: fs.readContentFromFile("/file.txt") == "hello",
            id="empty_content_is_noop",
        ),
        # sad path / invalid paths
        pytest.param([], "/a/b/     f", "x", False, None, id="whitespace_in_segment"),
        pytest.param([], "ab/c", "x", False, None, id="missing_leading_slash"),
        pytest.param([], "/a/b///c", "x", False, None, id="consecutive_slashes"),
    ],
)
def test_add_content_to_file(fs, setup, file_path, content, expected, verify):
    _run(fs, setup)
    assert fs.addContentToFile(file_path, content) is expected
    if verify is not None:
        assert verify(fs)


@pytest.mark.parametrize(
    "setup, path, expected",
    [
        # happy path
        pytest.param([("addContentToFile", ("/file.txt", "hello world"))], "/file.txt", "hello world", id="reads_written_content"),
        pytest.param([("addContentToFile", ("/file.txt", ""))], "/file.txt", "", id="empty_content"),
        pytest.param(
            [("addContentToFile", ("/a/b/c/file.txt", "nested content"))],
            "/a/b/c/file.txt",
            "nested content",
            id="nested_file",
        ),
        # sad path
        pytest.param([], "/does/not/exist.txt", None, id="nonexistent_path"),
        pytest.param([], "ab/c", None, id="missing_leading_slash"),
        pytest.param([], "/a/b/     f", None, id="whitespace_in_segment"),
        pytest.param([], "/a/b///c", None, id="consecutive_slashes"),
        pytest.param([("mkdir", ("/a/b",))], "/a/b", None, id="path_is_directory"),
    ],
)
def test_read_content_from_file(fs, setup, path, expected):
    _run(fs, setup)
    assert fs.readContentFromFile(path) == expected


@pytest.mark.parametrize(
    "setup, path, expected",
    [
        # happy path
        pytest.param([], "", [], id="empty_root"),
        pytest.param(
            [("mkdir", ("/b",)), ("mkdir", ("/a",)), ("addContentToFile", ("/c.txt", "x"))],
            "",
            ["a", "b", "c.txt"],
            id="root_lists_sorted_entries",
        ),
        pytest.param(
            [("mkdir", ("/a/b/c",)), ("mkdir", ("/a/b/d",))],
            "/a/b",
            ["c", "d"],
            id="lists_only_immediate_children",
        ),
        pytest.param([("addContentToFile", ("/a/file.txt", "content"))], "/a/file.txt", ["file.txt"], id="ls_on_file"),
        pytest.param([("mkdir", ("/a",))], "/a", [], id="empty_directory"),
        # sad path
        pytest.param([], "/does/not/exist", None, id="nonexistent_path"),
        pytest.param([], "ab/c", None, id="missing_leading_slash"),
        pytest.param([], "/a/b/     f", None, id="whitespace_in_segment"),
        pytest.param([], "/a/b///c", None, id="consecutive_slashes"),
    ],
)
def test_ls(fs, setup, path, expected):
    _run(fs, setup)
    assert fs.ls(path) == expected
