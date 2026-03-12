import os
import pytest
from pathlib import Path
from tools.sovereign_citation_indexer import CitationIndexer

@pytest.fixture
def mock_config(tmp_path):
    config_path = tmp_path / "citation_config.yaml"
    config_content = {
        "root_dir": str(tmp_path),
        "output_file": str(tmp_path / "CITATION_INDEX.md"),
        "include_extensions": [".md", ".py"],
        "ignore_dirs": ["ignore_me"],
        "ignore_files": ["ignored.md"]
    }
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config_content, f)
    return str(config_path)

@pytest.fixture
def indexer(mock_config):
    return CitationIndexer(mock_config)

def test_extract_metadata_markdown_standard(indexer, tmp_path):
    md_file = tmp_path / "test.md"
    md_content = """# Test Title
Date: 2023-10-27

This is a test description.
"""
    md_file.write_text(md_content)

    metadata = indexer._extract_metadata(md_file)
    assert metadata["title"] == "Test Title"
    assert metadata["date"] == "2023-10-27"
    assert metadata["description"] == "This is a test description."

def test_extract_metadata_markdown_alternate_date(indexer, tmp_path):
    md_file = tmp_path / "test.md"
    md_content = """# Another Title
Published on October 2023

Description starts here.
"""
    md_file.write_text(md_content)

    metadata = indexer._extract_metadata(md_file)
    assert metadata["title"] == "Another Title"
    assert metadata["date"] == "October 2023"

def test_extract_metadata_markdown_no_h1(indexer, tmp_path):
    md_file = tmp_path / "no_h1.md"
    md_content = "Just some content without H1 header."
    md_file.write_text(md_content)

    metadata = indexer._extract_metadata(md_file)
    assert metadata["title"] == "no h1" # Fallback to filename stem
    assert metadata["date"] == "Unknown"
    assert metadata["description"] == "Just some content without H1 header."

def test_extract_metadata_markdown_no_date(indexer, tmp_path):
    md_file = tmp_path / "no_date.md"
    md_content = "# Title Only\nNo date here."
    md_file.write_text(md_content)

    metadata = indexer._extract_metadata(md_file)
    assert metadata["title"] == "Title Only"
    assert metadata["date"] == "Unknown"

def test_extract_metadata_markdown_weird_date_format(indexer, tmp_path):
    md_file = tmp_path / "weird_date.md"
    md_content = "# Title\nDate is 27/10/2023 which is not supported."
    md_file.write_text(md_content)

    metadata = indexer._extract_metadata(md_file)
    assert metadata["date"] == "Unknown"

def test_extract_metadata_python(indexer, tmp_path):
    py_file = tmp_path / "script.py"
    py_content = '"""Module docstring.\nExtended description."""\n\ndef main(): pass'
    py_file.write_text(py_content)

    metadata = indexer._extract_metadata(py_file)
    assert metadata["type"] == ".py"
    assert "Module docstring" in metadata["description"]

def test_extract_metadata_error_handling(indexer, tmp_path):
    # Test with a non-existent file path object (should trigger Exception in _extract_metadata)
    # Actually, _extract_metadata receives a Path object, if it doesn't exist, read_text fails.
    non_existent = tmp_path / "non_existent.md"

    metadata = indexer._extract_metadata(non_existent)
    # Should return defaults
    assert metadata["title"] == "non existent"
    assert metadata["description"] == "No description available."
    assert metadata["date"] == "Unknown"

def test_is_ignored(indexer, tmp_path):
    ignored_dir = tmp_path / "ignore_me"
    ignored_dir.mkdir()
    ignored_file_in_dir = ignored_dir / "file.md"

    assert indexer._is_ignored(ignored_dir) is True
    assert indexer._is_ignored(ignored_file_in_dir) is True

    ignored_file = tmp_path / "ignored.md"
    assert indexer._is_ignored(ignored_file) is True

    normal_file = tmp_path / "normal.md"
    assert indexer._is_ignored(normal_file) is False
