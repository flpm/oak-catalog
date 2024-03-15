"""Classes that collect data in the catalog entries."""

from datetime import date
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class EntryData(BaseModel):
    """Represent a generic entry in the catalog."""

    entry_id: str = Field(min_length=1)
    entry_type: Union[
        Literal['link'], Literal['audiobook'], Literal['book'], Literal['list']
    ]
    format: str | None = None

    title: str = Field(min_length=1)
    subtitle: str | None = None
    full_title: str | None = None

    description: str | None = None
    summary: str | None = None

    cover_filename: str | None = None
    cover_url: str | None = None

    entry_date: date | str | None = None

    def __hash__(self) -> int:
        """
        Return the hash of the entry ID.

        Returns
        -------
        int
            The hash of the entry ID.
        """
        return self.entry_id.__hash__()

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


class ContentEntryData(EntryData):
    """Represent a content entry in the catalog."""

    author: List[str] = Field(default_factory=list)
    publisher: str | None = None
    published_date: date | str | None = None

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


class LinkEntryData(ContentEntryData):
    """Represent a link entry in the catalog."""

    url: str
    domain: str

    protected_fields: list = Field(
        default_factory=lambda: ['entry_id', 'entry_type', 'protected_fields', 'url']
    )


class AudiobookEntryData(ContentEntryData):
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


class BookEntryData(ContentEntryData):
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


class ListEntryData(EntryData):
    """Represent a list entry in the catalog."""

    type_count: dict = Field(default_factory=dict)
    protected_fields: list = Field(
        default_factory=lambda: [
            'entry_id',
            'entry_type',
            'protected_fields',
        ]
    )
    list_items: List[BookEntryData | AudiobookEntryData | LinkEntryData] = Field(
        default_factory=list
    )

    def append(self, entry: EntryData):
        """
        Append an entry to the list.

        Parameters
        ----------
        entry : EntryData
            The entry to append.
        """
        self.list_items.append(entry)

    def remove(self, entry: EntryData):
        """
        Remove an entry from the list.

        Parameters
        ----------
        entry : EntryData
            The entry to remove.
        """
        self.list_items.remove(entry)

    def __getitem__(self, index: int):
        """
        Get an item from the list.

        Parameters
        ----------
        index : int
            The index of the item.

        Returns
        -------
        EntryData
            The item.
        """
        return self.list_items[index]

    def __len__(self):
        """
        Get the length of the list.

        Returns
        -------
        int
            The length of the list.
        """
        return len(self.list_items)

    def __iter__(self):
        """
        Iterate over the list.

        Yields
        ------
        EntryData
            The items in the list.
        """
        for item in self.list_items:
            yield item
