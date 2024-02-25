"""Classes that collect data in the catalog entries."""

from datetime import date
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class EntryData(BaseModel):
    """Represent a generic entry in the catalog."""

    entry_id: str = Field(min_length=1)
    entry_type: Union[Literal['link'], Literal['audiobook'], Literal['book']]
    format: str

    title: str = Field(min_length=1)
    subtitle: str | None = None
    full_title: str | None = None

    author: List[str] = Field(default_factory=list)
    publisher: str
    published_date: date | str | None = None

    description: str | None = None
    summary: str | None = None

    language: List[str] | None = Field(default_factory=lambda: ['English'])
    theme: str | None = None
    topics: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    entry_creation_date: date = Field(default_factory=date.today)
    read_date: date | str | None = None

    source: str = None
    protected_fields: list = Field(
        default_factory=lambda: [
            'entry_id',
            'entry_type',
            'protected_fields',
            'tags',
            'theme',
            'summary',
            'description',
        ]
    )

    cover_filename: str | None = None
    cover_url: str | None = None

    def merge(
        self,
        entry: 'EntryData',
        prevent_overwrite: bool = False,
        protected: list = None,
    ):
        """
        Merge the given entry into this entry.

        Parameters
        ----------
        entry : EntryData
            The entry to merge into this entry.
        prevent_overwrite : bool, optional
            Whether to overwrite existing non-null values, by default False.
        protected : list, optional
            A list of fields that should not be overwritten, by default the list of manually added fields.

        Returns
        -------
        bool
            Whether the entry was changed.
        """
        if protected is None:
            protected = self.protected_fields or []
        if 'protected_fields' not in protected:
            protected.extend(['protected_fields'])

        if entry.entry_id and entry.entry_id != self.entry_id:
            raise ValueError('Cannot merge entries with different IDs.')

        changed = False
        for field in self.model_fields.keys():
            if this_one := getattr(self, field):
                other_one = getattr(entry, field)
                if isinstance(this_one, list):
                    this_one = set(this_one)
                if isinstance(other_one, list):
                    other_one = set(other_one)
                if other_one and this_one != other_one and prevent_overwrite:
                    print(
                        f'{self.entry_id} - Prevented overwrite {field}: {this_one} ==> {other_one}'
                    )
            if field in protected:
                continue
            if getattr(entry, field) != getattr(self, field):
                setattr(self, field, getattr(entry, field))
                changed = True
        return changed


class LinkEntryData(EntryData):
    """Represent a link entry in the catalog."""

    url: str
    domain: str

    protected_fields: list = Field(
        default_factory=lambda: ['entry_id', 'entry_type', 'protected_fields', 'url']
    )


class AudiobookEntryData(EntryData):
    """Represent an audiobook entry in the catalog."""

    narrator: List[str] = Field(default_factory=list)
    asin: str = None
    length: str = None
    purchase_date: date | str | None = None

    protected_fields: list = Field(
        default_factory=lambda: [
            'entry_id',
            'entry_type',
            'protected_fields',
            'asin',
            'tags',
            'theme',
            'summary',
            'description',
        ]
    )


class BookEntryData(EntryData):
    """Represent a book entry in the catalog."""

    isbn: str | None = None
    length: str | None = None
    purchase_date: date | str | None = None

    protected_fields: list = Field(
        default_factory=lambda: [
            'entry_id',
            'entry_type',
            'protected_fields',
            'isbn',
            'tags',
            'theme',
            'summary',
            'description',
        ]
    )
