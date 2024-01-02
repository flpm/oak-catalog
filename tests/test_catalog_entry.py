"""Tests for the CatalogEntry class."""

from datetime import date

import pydantic
import pytest
from oak_catalog.catalog_entry import CatalogEntry


class TestCatalogEntry:
    """Test the CatalogEntry class."""

    def test_creation(self):
        """Test that a CatalogEntry can be created."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        assert entry.entry_id == 'test_id'
        assert entry.entry_type == 'book'
        assert entry.title == 'test_title'
        assert entry.author == ['test_author']

    def test_creation_with_invalid_entry_type(self):
        """Test that an invalid entry type raises an exception."""
        with pytest.raises(pydantic.ValidationError):
            CatalogEntry(
                entry_id='test_id',
                entry_type='invalid_type',
                title='test_title',
                author=['test_author'],
            )

    def test_creation_with_invalid_entry_id(self):
        """Test that an invalid entry ID raises an exception."""
        with pytest.raises(pydantic.ValidationError):
            CatalogEntry(
                entry_id='',
                entry_type='book',
                title='test_title',
                author=['test_author'],
            )

    def test_creation_with_invalid_title(self):
        """Test that an invalid title raises an exception."""
        with pytest.raises(pydantic.ValidationError):
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='',
                author=['test_author'],
            )

    def test_creation_with_invalid_author(self):
        """Test that an invalid author raises an exception."""
        with pytest.raises(pydantic.ValidationError):
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='test_title',
                author=[],
            )

    def test_creation_with_all_attributes(self):
        """Test that a CatalogEntry can be created with all attributes."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            isbn='test_isbn',
            asin='test_asin',
            url='test_url',
            title='test_title',
            author=['test_author'],
            subtitle='test_subtitle',
            full_title='test_full_title',
            narrator=['test_narrator'],
            description='test_description',
            format='test_format',
            length='test_length',
            language=['test_language'],
            publisher='test_publisher',
            publishing_date='2020-01-01',
            theme='test_theme',
            topics=['test_topic'],
            subjects=['test_subject'],
            tags=['test_tag'],
            location='test_location',
            purchase_date='2020-01-01',
            entry_creation_date='2020-01-01',
            cover_filename='test_cover_filename',
            markdown_filename='test_markdown_filename',
            site_url='test_site_url',
        )
        assert entry.entry_id == 'test_id'
        assert entry.entry_type == 'book'
        assert entry.isbn == 'test_isbn'
        assert entry.asin == 'test_asin'
        assert entry.url == 'test_url'
        assert entry.title == 'test_title'
        assert entry.author == ['test_author']
        assert entry.subtitle == 'test_subtitle'
        assert entry.full_title == 'test_full_title'
        assert entry.narrator == ['test_narrator']
        assert entry.description == 'test_description'
        assert entry.format == 'test_format'
        assert entry.length == 'test_length'
        assert entry.language == ['test_language']
        assert entry.publisher == 'test_publisher'
        assert entry.publishing_date == date(2020, 1, 1)
        assert entry.theme == 'test_theme'
        assert entry.topics == ['test_topic']
        assert entry.subjects == ['test_subject']
        assert entry.tags == ['test_tag']
        assert entry.location == 'test_location'
        assert entry.purchase_date == date(2020, 1, 1)
        assert entry.entry_creation_date == date(2020, 1, 1)
        assert entry.cover_filename == 'test_cover_filename'
        assert entry.markdown_filename == 'test_markdown_filename'
        assert entry.site_url == 'test_site_url'

    def test_merge_fails(self):
        """Test that a CatalogEntry can be merged."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        with pytest.raises(pydantic.ValidationError):
            entry.merge(
                CatalogEntry(
                    entry_id='test_id',
                    entry_type='invalid_type',
                    title='test_title',
                    author=['test_author'],
                )
            )

    def test_merge_overwrite_no_protection(self):
        """Test that a CatalogEntry can be merged without protection."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        entry.merge(
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='test_title',
                subtitle='test_subtitle',
                full_title='test_full_title',
                author=['test_author'],
                narrator=['test_narrator'],
                description='test_description',
                format='test_format',
                length='test_length',
                language=['test_language'],
                publisher='test_publisher',
                publishing_date='2020-01-01',
                theme='test_theme',
                topics=['test_topic'],
                subjects=['test_subject'],
                tags=['test_tag'],
                location='test_location',
                purchase_date='2020-01-01',
                entry_creation_date='2020-01-01',
                cover_filename='test_cover_filename',
                markdown_filename='test_markdown_filename',
                site_url='test_site_url',
            ),
            overwrite=True,
            protected=[],
        )
        assert entry.entry_id == 'test_id'
        assert entry.entry_type == 'book'
        assert entry.title == 'test_title'
        assert entry.author == ['test_author']
        assert entry.subtitle == 'test_subtitle'
        assert entry.full_title == 'test_full_title'
        assert entry.narrator == ['test_narrator']
        assert entry.description == 'test_description'
        assert entry.format == 'test_format'
        assert entry.length == 'test_length'
        assert entry.language == ['test_language']
        assert entry.publisher == 'test_publisher'
        assert entry.publishing_date == date(2020, 1, 1)
        assert entry.theme == 'test_theme'
        assert entry.topics == ['test_topic']
        assert entry.subjects == ['test_subject']
        assert entry.tags == ['test_tag']
        assert entry.location == 'test_location'
        assert entry.purchase_date == date(2020, 1, 1)
        assert entry.entry_creation_date == date(2020, 1, 1)
        assert entry.cover_filename == 'test_cover_filename'
        assert entry.markdown_filename == 'test_markdown_filename'
        assert entry.site_url == 'test_site_url'

    def test_merge_overwrite_with_protection(self):
        """Test that a CatalogEntry can be merged with protection."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            theme='original_theme',
            subjects=['oiginal_subject'],
            tags=['original_tag'],
            location='original_location',
            purchase_date='1999-01-01',
            author=['test_author'],
        )
        entry.merge(
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='test_title',
                subtitle='test_subtitle',
                full_title='test_full_title',
                author=['test_author'],
                narrator=['test_narrator'],
                description='test_description',
                format='test_format',
                length='test_length',
                language=['test_language'],
                publisher='test_publisher',
                publishing_date='2020-01-01',
                theme='test_theme',
                topics=['test_topic'],
                subjects=['test_subject'],
                tags=['test_tag'],
                location='test_location',
                purchase_date='2020-01-01',
                entry_creation_date='2020-01-01',
                cover_filename='test_cover_filename',
                markdown_filename='test_markdown_filename',
                site_url='test_site_url',
            ),
            overwrite=True,
        )
        assert entry.entry_id == 'test_id'
        assert entry.entry_type == 'book'
        assert entry.title == 'test_title'
        assert entry.author == ['test_author']
        assert entry.subtitle == 'test_subtitle'
        assert entry.full_title == 'test_full_title'
        assert entry.narrator == ['test_narrator']
        assert entry.description == 'test_description'
        assert entry.format == 'test_format'
        assert entry.length == 'test_length'
        assert entry.language == ['test_language']
        assert entry.publisher == 'test_publisher'
        assert entry.publishing_date == date(2020, 1, 1)
        assert entry.theme == 'original_theme'
        assert entry.topics == ['test_topic']
        assert entry.subjects == ['oiginal_subject']
        assert entry.tags == ['original_tag']
        assert entry.location == 'original_location'
        assert entry.purchase_date == date(1999, 1, 1)
        assert entry.entry_creation_date == date.today()
        assert entry.cover_filename == 'test_cover_filename'
        assert entry.markdown_filename == 'test_markdown_filename'
        assert entry.site_url == 'test_site_url'

    def test_merge_changed(self):
        """Test if the merge returned changed."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        changed = entry.merge(
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='test_title',
                subtitle='test_subtitle',
                full_title='test_full_title',
                author=['test_author'],
                narrator=['test_narrator'],
                description='test_description',
                format='test_format',
                length='test_length',
                language=['test_language'],
                publisher='test_publisher',
                publishing_date='2020-01-01',
                theme='test_theme',
                topics=['test_topic'],
                subjects=['test_subject'],
                tags=['test_tag'],
                location='test_location',
                purchase_date='2020-01-01',
                entry_creation_date='2020-01-01',
                cover_filename='test_cover_filename',
                markdown_filename='test_markdown_filename',
                site_url='test_site_url',
            ),
            overwrite=True,
        )
        assert changed

    def test_merge_not_changed(self):
        """Test if the merge entry did not change."""
        entry = CatalogEntry(
            entry_id='test_id',
            entry_type='book',
            title='test_title',
            author=['test_author'],
        )
        changed = entry.merge(
            CatalogEntry(
                entry_id='test_id',
                entry_type='book',
                title='test_title',
                author=['test_author'],
            ),
            overwrite=True,
        )
        assert not changed
