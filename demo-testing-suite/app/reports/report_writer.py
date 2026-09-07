"""Writes plain-text report files to disk.

Demonstrates why pytest ships a built-in tmp_path fixture: tests that
touch the filesystem should never write into the real project directory
or any shared location. See tests/reports/test_report_writer.py.
"""


def save_report(directory, filename, content):
    """Write ``content`` to ``directory / filename`` and return the path.

    Args:
        directory: A pathlib.Path to an existing, writable directory. In
            tests this should always be pytest's ``tmp_path`` fixture --
            never a real project folder.
        filename: The file's name (not a full path).
        content: Text to write.

    Returns:
        The pathlib.Path that was written.
    """
    path = directory / filename
    path.write_text(content)
    return path
