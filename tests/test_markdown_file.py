"""Tests for MarkdownFile class."""

from unittest.mock import mock_open, patch

from oak_catalog.markdown_file import MarkdownFile, OmnivoreMarkdownFile


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
        assert (
            markdown_file.raw_content == '---\ntitle: Test Title\n---\nTest Content\n'
        )
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
        assert markdown_file.raw_content == ''
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
        assert markdown_file.raw_content == 'Test Content\n'
        assert markdown_file.content == 'Test Content'
        assert markdown_file.frontmatter == {}


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
            markdown_file.raw_content
            == '---\ntitle: Test Title\n---\n# Test Title\n[Read on Omnivore]\n\nLink to Omnivore\n\n## Highlights\n\nFirst highlight\n\nSecond highlight'
        )
        assert (
            markdown_file.content
            == '# Test Title\n[Read on Omnivore]\n\nLink to Omnivore\n\n## Highlights\n\nFirst highlight\n\nSecond highlight'
        )
        assert markdown_file.frontmatter == {'title': 'Test Title'}
        assert markdown_file.highlights == [
            'First highlight',
            'Second highlight',
        ]

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
        assert (
            markdown_file.raw_content
            == '---\ntitle: Test Title\n---\n# Test Title\n[Read on Omnivore]'
        )
        assert markdown_file.content == '# Test Title\n[Read on Omnivore]'
        assert markdown_file.frontmatter == {'title': 'Test Title'}
        assert markdown_file.highlights == []
