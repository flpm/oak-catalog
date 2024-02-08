"""Tests for MarkdownFile class."""

import os
from unittest.mock import mock_open, patch

import pytest
from oak_catalog.markdown_file import (
    CatalogEntryMarkdownFile,
    MarkdownFile,
    OmnivoreMarkdownFile,
)


class TestMarkdownFile:
    """Test the MarkdownFile class."""

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='---\ntitle: Test Title\n---\nTest Content\n',
    )
    def test_read(self, mock_file):
        """Test that a Markdown file can be read."""
        markdown_file = MarkdownFile('tests/test_data/test_markdown_file.md')
        mock_file.assert_called_once_with('tests/test_data/test_markdown_file.md', 'r')
        assert markdown_file.filename == 'tests/test_data/test_markdown_file.md'
        assert markdown_file.content == 'Test Content'
        assert markdown_file.frontmatter == {'title': 'Test Title'}

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='---\ntitle: Test Title\n---\nTest Content\n',
    )
    def test_read_new_file(self, mock_file):
        """Test creating a Markdown for a new file that does not exist."""
        mock_file.side_effect = FileNotFoundError()
        markdown_file = MarkdownFile('tests/test_data/non_existent.md')
        mock_file.assert_called_once_with('tests/test_data/non_existent.md', 'r')
        assert markdown_file.filename == 'tests/test_data/non_existent.md'
        assert markdown_file.content == ''
        assert markdown_file.frontmatter == {}

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='Test Content\n',
    )
    def test_read_no_frontmatter(self, mock_file):
        """Test that a Markdown file can be read with no frontmatter."""
        markdown_file = MarkdownFile(
            'tests/test_data/test_markdown_file_no_frontmatter.md'
        )
        assert (
            markdown_file.filename
            == 'tests/test_data/test_markdown_file_no_frontmatter.md'
        )
        assert markdown_file.content == 'Test Content'
        assert markdown_file.frontmatter == {}

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='---\ntitle: "title"\nauthors: ["author 1", "author 2"]\n---\ncontent',
    )
    def test_to_dict(self, mock_file):
        """Test that a Markdown file can be converted to a dictionary."""
        markdown_file = MarkdownFile('tests/test_data/test_file_1.md')
        assert mock_file.call_count == 1
        assert mock_file.call_args_list[0][0][0] == 'tests/test_data/test_file_1.md'
        assert markdown_file.to_dict() == {
            'filename': 'tests/test_data/test_file_1.md',
            'content': 'content',
            'frontmatter': {'title': 'title', 'authors': ['author 1', 'author 2']},
        }

    def test_write(self):
        """Test that a Markdown file can be written."""
        markdown_file = MarkdownFile('tests/test_data/test_file_1.md')
        markdown_file.filename = 'tests/test_data/test_file_1.md.temp'
        markdown_file.write()
        markdown_file_temp = MarkdownFile('tests/test_data/test_file_1.md.temp')
        for key, value in markdown_file.to_dict().items():
            assert markdown_file_temp.to_dict()[key] == value
        os.remove('tests/test_data/test_file_1.md.temp')


class TestOmnivoreMarkdownFile:
    """Test the OmnivoreMarkdownFile class."""

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='---\ntitle: Test Title\n---\n# Test Title\n[Read on Omnivore]\n\nLink to Omnivore\n\n## Highlights\n\nFirst highlight\n\nSecond highlight',
    )
    def test_read_omnivore_file_with_highlights(self, mock_file):
        """Test that an Omnivore Markdown file with highlights can be read."""
        markdown_file = OmnivoreMarkdownFile(
            'tests/test_data/test_omnivore_markdown_file.md'
        )
        mock_file.assert_called_once_with(
            'tests/test_data/test_omnivore_markdown_file.md', 'r'
        )
        assert (
            markdown_file.filename == 'tests/test_data/test_omnivore_markdown_file.md'
        )
        assert (
            markdown_file.content
            == '# Test Title\n[Read on Omnivore]\n\nLink to Omnivore\n\n## Highlights\n\nFirst highlight\n\nSecond highlight'
        )
        assert markdown_file.frontmatter == {
            'title': 'Test Title',
            'highlights': [
                'First highlight',
                'Second highlight',
            ],
        }

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='---\ntitle: Test Title\n---\n# Test Title\n[Read on Omnivore]',
    )
    def test_read_omnivore_file_without_highlights(self, mock_file):
        """Test that an Omnivore Markdown file without highlights can be read."""
        markdown_file = OmnivoreMarkdownFile(
            'tests/test_data/test_omnivore_markdown_file.md'
        )
        mock_file.assert_called_once_with(
            'tests/test_data/test_omnivore_markdown_file.md', 'r'
        )
        assert (
            markdown_file.filename == 'tests/test_data/test_omnivore_markdown_file.md'
        )

        assert markdown_file.content == '# Test Title\n[Read on Omnivore]'
        assert markdown_file.frontmatter == {'title': 'Test Title', 'highlights': []}


class TestCatalogEntryMarkdownFile:
    """Test the CatalogEntryMarkdownFile class."""

    def test_read(self):
        """Test that a catalog entry Markdown file can be read."""
        markdown_file = CatalogEntryMarkdownFile(
            'tests/test_data/test_catalog_entry.md'
        )
        assert markdown_file.filename == 'tests/test_data/test_catalog_entry.md'

    def test_merge_read_protected_field_default(self):
        """Test that a catalog entry Markdown file fails when merged with a change in protected field."""
        markdown_file = CatalogEntryMarkdownFile(
            'tests/test_data/test_catalog_entry.md'
        )
        markdown_file.filename = 'tests/test_data/test_catalog_entry_modif.md'
        with pytest.raises(ValueError):
            markdown_file.read()

    def test_merge_read_protected_field_defined(self):
        """Test that a catalog entry Markdown file fails when merged with a change in protected field."""
        markdown_file = CatalogEntryMarkdownFile(
            'tests/test_data/test_catalog_entry.md'
        )
        markdown_file.filename = 'tests/test_data/test_catalog_entry_modif_protected.md'
        with pytest.raises(ValueError):
            markdown_file.read()

    def test_merge_read_unprotected_field(self):
        """Test that a catalog entry Markdown file can be read and merged."""
        markdown_file = CatalogEntryMarkdownFile(
            'tests/test_data/test_catalog_entry.md'
        )
        markdown_file.filename = (
            'tests/test_data/test_catalog_entry_modif_unprotected.md'
        )
        markdown_file.protect_fields([])
        markdown_file.allow_overwrite = True
        assert markdown_file.catalog_entry.protected_fields == []
        markdown_file.read()
        assert markdown_file.catalog_entry.title == markdown_file.frontmatter['title']
