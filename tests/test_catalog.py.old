"""Test the Catalog class."""

from datetime import date
from unittest.mock import mock_open, patch

import pytest
from oak_catalog.catalog import Catalog
from oak_catalog.catalog_entry import CatalogEntry


class TestCatalog:
    """Test the Catalog class."""

    def test_setitem_with_dict(self):
        """Test that a dict can be used to create a CatalogEntry."""
        catalog = Catalog()
        catalog['test_id'] = {
            'entry_id': 'test_id',
            'entry_type': 'book',
            'title': 'test_title',
            'author': ['test_author'],
        }
        assert len(catalog) == 1
        assert catalog['test_id'].entry_id == 'test_id'
        assert catalog['test_id'].entry_type == 'book'
        assert catalog['test_id'].title == 'test_title'
        assert catalog['test_id'].author == ['test_author']

    def test_setitem_with_catalog_entry(self):
        """Test that a CatalogEntry can be used to create a CatalogEntry."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        assert len(catalog) == 1
        assert catalog['test_id'].entry_id == 'test_id'
        assert catalog['test_id'].entry_type == 'book'
        assert catalog['test_id'].title == 'test_title'
        assert catalog['test_id'].author == ['test_author']

    def test_getitem_existing_entry(self):
        """Test that an existing entry can be retrieved."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        retrieved_entry = catalog['test_id']
        assert retrieved_entry is not None
        assert retrieved_entry.entry_id == 'test_id'
        assert retrieved_entry.entry_type == 'book'
        assert retrieved_entry.title == 'test_title'
        assert retrieved_entry.author == ['test_author']

    def test_getitem_non_existent_entry(self):
        """Test that a non-existent entry returns None."""
        catalog = Catalog()
        retrieved_entry = catalog['non_existent_id']
        assert retrieved_entry is None

    def test_iter_no_entries(self):
        """Test that an empty catalog returns an empty iterator."""
        catalog = Catalog()
        assert list(catalog) == []

    def test_iter_with_entries(self):
        """Test that a catalog returns an iterator with all entries."""
        catalog = Catalog()
        entry1 = CatalogEntry(
            entry_id='test_id1',
            entry_type='book',
            title='test_title1',
            author=['test_author1'],
        )
        entry2 = CatalogEntry(
            entry_id='test_id2',
            entry_type='book',
            title='test_title2',
            author=['test_author2'],
        )
        catalog['test_id1'] = entry1
        catalog['test_id2'] = entry2
        assert list(catalog) == [entry1, entry2]

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='{"entries": {"test_id": {"entry_id": "test_id", "entry_type": "book", "title": "test_title", "author": ["test_author"]}}}',
    )
    def test_load(self, mock_file):
        """Test that a catalog can be loaded from a file."""
        catalog = Catalog.load('test.json')
        assert isinstance(catalog, Catalog)
        assert len(catalog) == 1
        assert catalog['test_id'].entry_id == 'test_id'
        mock_file.assert_called_once_with('test.json', 'r')

    @patch('builtins.open', new_callable=mock_open)
    def test_load_file_not_found(self, mock_file):
        """Test that a catalog raises a FileNotFoundError error if the catalog file does not exist."""
        mock_file.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match='Catalog file not found.'):
            Catalog.load('non_existent.json')

    @patch('builtins.open', new_callable=mock_open)
    def test_save(self, mock_file):
        """Test that a catalog can be saved to a file."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        catalog.save()
        mock_file.assert_called_once_with('./work/catalog.json', 'w')
        mock_file().write.assert_called_once()

    @patch('builtins.open', new_callable=mock_open)
    def test_save_with_filename(self, mock_file):
        """Test that a catalog can be saved to a file with a filename."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        catalog.save('test.json')
        mock_file.assert_called_once_with('test.json', 'w')
        mock_file().write.assert_called_once()

    def test_merge_no_intersection(self):
        """Test that a catalog can be merged with another catalog with overwrite."""
        catalog1 = Catalog()
        catalog2 = Catalog()
        entry1 = CatalogEntry(
            entry_id='test_id1',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        entry2 = CatalogEntry(
            entry_id='test_id2',
            entry_type='book',
            title='test_title2',
            author=['test_author2'],
        )
        catalog1['test_id1'] = entry1
        catalog2['test_id2'] = entry2
        catalog1.merge(catalog2)
        assert len(catalog1) == 2
        assert catalog1['test_id1'].entry_id == 'test_id1'
        assert catalog1['test_id1'].entry_type == 'book'
        assert catalog1['test_id1'].title == 'test_title'
        assert catalog1['test_id1'].author == ['test_author']
        assert catalog1['test_id2'].entry_id == 'test_id2'
        assert catalog1['test_id2'].entry_type == 'book'
        assert catalog1['test_id2'].title == 'test_title2'
        assert catalog1['test_id2'].author == ['test_author2']

    def test_merge_intersection(self):
        """Test that a catalog merges correctly when they overlap."""
        catalog1 = Catalog()
        catalog2 = Catalog()
        entry1 = CatalogEntry(
            entry_id='test_id1',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        entry2 = CatalogEntry(
            entry_id='test_id1',
            entry_type='book',
            title='test_title2',
            author=['test_author2'],
        )
        catalog1['test_id1'] = entry1
        catalog2['test_id2'] = entry2
        catalog1.merge(catalog2, overwrite=True)
        assert len(catalog1) == 1
        assert catalog1['test_id1'].entry_id == 'test_id1'
        assert catalog1['test_id1'].entry_type == 'book'
        assert catalog1['test_id1'].title == 'test_title2'
        assert catalog1['test_id1'].author == ['test_author2']

    def test_backup_filename(self):
        """Test that a catalog can be backed up with a filename."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        with patch.object(Catalog, 'save', return_value=None) as mock_save:
            filename = catalog.backup('test_backup.json')
        mock_save.assert_called_once()
        mock_save.assert_called_with(filename)

    def test_backup_default_filename(self):
        """Test that a catalog can be backed up with a filename."""
        catalog = Catalog()
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        catalog['test_id'] = entry
        with patch.object(Catalog, 'save', return_value=None) as mock_save:
            filename = catalog.backup()
        mock_save.assert_called_once()
        mock_save.assert_called_with(filename)
        assert filename.split('/')[-1].split('_')[0] == date.today().isoformat()
