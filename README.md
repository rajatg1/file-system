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
