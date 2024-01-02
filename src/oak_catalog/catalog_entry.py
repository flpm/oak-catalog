"""Define the CatalogEntry class, which represents a single entry in the catalog."""

from datetime import date
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class CatalogEntry(BaseModel):
    """
    Class to represent a single entry in the catalog.

    Attributes
    ----------
    entry_id : str
        The ID of the entry.
    entry_type : Literal["article", "audiobook", "book"]
        The type of the entry.
    isbn : str, optional
        The ISBN of the entry.
    asin : str, optional
        The ASIN of the entry.
    url : str, optional
        The URL of the entry.
    title : str
        The title of the entry.
    author : List[str]
        The author(s) of the entry.
    subtitle : str, optional
        The subtitle of the entry.
    full_title : str, optional
        The full title of the entry.
    narrator : List[str], optional
        The narrator(s) of the entry.
    description : str, optional
        The description of the entry.
    format : str, optional
        The format of the entry.
    length : str, optional
        The length of the entry.
    language : List[str], optional
        The language(s) of the entry.
    publisher : str, optional
        The publisher of the entry.
    publishing_date : date, optional
        The publishing date of the entry.
    theme : str, optional
        The theme of the entry.
    topics : List[str], optional
        The topics of the entry.
    subjects : List[str], optional
        The subject(s) of the entry.
    tags : List[str], optional
        The tags of the entry.
    note : str, optional
        The note content for the entry.
    location : str, optional
        The location of the entry.
    purchase_date : date, optional
        The purchase date of the entry.
    entry_creation_date : date, optional
        The creation date of the entry.
    cover_filename : str, optional
        The filename of the cover image of the entry.
    markdown_filename : str, optional
        The filename of the markdown file of the entry.
    site_url : str, optional
        The URL of the entry in the site.
    """

    entry_id: str = Field(min_length=1)
    entry_type: Union[Literal['article'], Literal['audiobook'], Literal['book']]

    isbn: str = None
    asin: str = None
    url: str = None

    title: str = Field(min_length=1)
    author: List[str] = Field(min_length=1)
    subtitle: str = None
    full_title: str = None
    narrator: List[str] = Field(default_factory=list)
    description: str = None
    format: str = None
    length: str = None
    language: List[str] = Field(default_factory=lambda: ['English'])
    publisher: str = None
    publishing_date: date = None

    theme: str = None
    topics: List[str] = Field(default_factory=list)
    subjects: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    location: str = 'New York'
    purchase_date: date = None
    note: str = None

    entry_creation_date: date = Field(default_factory=date.today)

    cover_filename: str = None
    markdown_filename: str = None
    site_url: str = None

    def set_field(self, field: str, value: str, override: bool = False):
        """
        Set the given field to the given value.

        Parameters
        ----------
        field : str
            The field to set.
        value : str
            The value to set the field to.
        override : bool, optional
            Whether to override existing values, by default False.

        Returns
        -------
        bool
            Whether the field was set.
        """
        if getattr(self, field) and not override:
            return False
        setattr(self, field, value)
        return True

    def merge(
        self, entry: 'CatalogEntry', overwrite: bool = False, protected: list = None
    ):
        """
        Merge the given entry into this entry.

        Parameters
        ----------
        entry : CatalogEntry
            The entry to merge into this entry.
        overwrite : bool, optional
            Whether to overwrite existing values, by default False.
        protected : list, optional
            A list of fields that should not be overwritten, by default the list of manually added fields.
        """
        if protected is None:
            protected = [
                'entry_type',
                'entry_creation_date',
                'theme',
                'subjects',
                'tags',
                'location',
                'purchase_date',
                'note',
            ]

        if entry.entry_id and entry.entry_id != self.entry_id:
            raise ValueError('Cannot merge entries with different IDs.')

        for field in (
            'isbn',
            'asin',
            'url',
            'title',
            'author',
            'subtitle',
            'full_title',
            'narrator',
            'description',
            'format',
            'length',
            'language',
            'publisher',
            'publishing_date',
            'theme',
            'topics',
            'subjects',
            'tags',
            'location',
            'purchase_date',
            'entry_creation_date',
            'cover_filename',
            'markdown_filename',
            'site_url',
        ):
            if getattr(self, field):
                if getattr(entry, field) and not overwrite:
                    raise ValueError(f'Cannot overwrite existing {field}.')
            if field in protected:
                continue
            setattr(self, field, getattr(entry, field))
