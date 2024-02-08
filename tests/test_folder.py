"""Tests for the Folder class."""

from pathlib import Path

from oak_catalog.folder import Folder


class TestFolder:
    """Tests for the Folder class."""

    def test_creation(self):
        """Test that a Folder can be created."""
        folder = Folder('tests/test_data')
        assert folder.path_raw == 'tests/test_data'
        assert folder.path == Path('tests/test_data')

    def test_repr(self):
        """Test that the string representation of a Folder is correct."""
        folder = Folder('tests/test_data_non_existent')
        assert repr(folder) == 'Folder(path=tests/test_data_non_existent non-existent)'

    def test_repr_exists(self):
        """Test that the string representation of a Folder is correct."""
        folder = Folder('tests/test_data_dummy_folder')
        folder.create()
        assert repr(folder) == 'Folder(path=tests/test_data_dummy_folder exists)'
        folder.delete()

    def test_for_each(self):
        """Test that a function can be called for each file in a folder."""
        folder = Folder('tests/test_data')
        files = sorted(folder.for_each(str))
        assert len(files) == 6
        assert files[0] == 'tests/test_data/test_catalog_entry.md'
        assert files[1] == 'tests/test_data/test_catalog_entry_modif.md'
        assert files[2] == 'tests/test_data/test_catalog_entry_modif_protected.md'
        assert files[3] == 'tests/test_data/test_catalog_entry_modif_unprotected.md'
        assert files[4] == 'tests/test_data/test_file_1.md'
        assert files[5] == 'tests/test_data/test_file_2.md'
