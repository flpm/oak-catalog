"""Class to represent the Oak catalog."""

import json
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Dict, Union

from pydantic import BaseModel, Field

from .catalog_entry import CatalogEntry


class Catalog(BaseModel):
    """
    Class to represent the Oak catalog.

    Attributes
    ----------
    entries : Dict[str, CatalogEntry]
        The entries in the catalog.
    load_date : datetime
        The date the catalog was loaded.
    creation_date : datetime
        The date the catalog was created.
    modification_date : datetime
        The date the catalog was last modified.
    catalog_filename : ClassVar[str]
        The filename of the catalog.
    backup_location : ClassVar[str]
        The location to store backups.
    markdown_location : ClassVar[str]
        The location to store markdown files.
    cover_location : ClassVar[str]
        The location to store cover images.
    """

    entries: Dict[str, CatalogEntry] = Field(default_factory=dict)

    load_date: datetime = Field(default_factory=datetime.now)

    creation_date: datetime = Field(default_factory=datetime.now)
    modification_date: datetime = Field(default_factory=datetime.now)

    catalog_filename: ClassVar[str] = './work/catalog.json'
    backup_location: ClassVar[str] = './work/backup'
    markdown_location: ClassVar[str] = './output/markdown'
    cover_location: ClassVar[str] = './output/covers'

    def remove(self, entry_id: str):
        """
        Remove an entry from the catalog.

        Parameters
        ----------
        entry_id : str
            The ID of the entry to remove.
        """
        self.entries.pop(entry_id)

    def __getitem__(self, entry_id: str) -> CatalogEntry:
        """
        Get an entry from the catalog.

        Parameters
        ----------
        entry_id : str
            The ID of the entry to get.

        Returns
        -------
        CatalogEntry
            The entry with the given ID.
        """
        return self.entries.get(entry_id)

    def __setitem__(self, entry_id: str, entry: Union[dict, CatalogEntry]):
        """
        Add an entry to the catalog.

        Parameters
        ----------
        entry_id : str
            The ID of the entry to add.
        entry : Union[dict, CatalogEntry]
            The entry to add.

        Raises
        ------
        TypeError
            If the entry is not a dict or CatalogEntry.
        """
        if isinstance(entry, dict):
            entry = CatalogEntry(**entry)
        self.entries[entry.entry_id] = entry

    def __iter__(self):
        """
        Iterate over the catalog.

        Returns
        -------
        Iterator[CatalogEntry]
            The entries in the catalog.
        """
        return iter(self.entries.values())

    def __len__(self):
        """
        Get the number of entries in the catalog.

        Returns
        -------
        int
            The number of entries in the catalog.
        """
        return len(self.entries)

    def __contains__(self, entry_id: str):
        """
        Check if an entry is in the catalog.

        Parameters
        ----------
        entry_id : str
            The ID of the entry to check for.

        Returns
        -------
        bool
            True if the entry is in the catalog, False otherwise.
        """
        return entry_id in self.entries

    def __repr__(self):
        """
        Get a string representation of the catalog.

        Returns
        -------
        str
            A string representation of the catalog.
        """
        return f'Catalog(size={len(self.entries)})'

    def save(self, catalog_filename: str = None):
        """
        Save the catalog to a JSON file.

        Parameters
        ----------
        catalog_filename : str, optional
            The filename to save the catalog to, by default None.

        Raises
        ------
        RuntimeError
            If there is an error saving the catalog.
        """

        catalog_filename = catalog_filename or self.catalog_filename

        try:
            Path(catalog_filename).parent.mkdir(parents=True, exist_ok=True)
            with open(catalog_filename, 'w') as fp:
                fp.write(self.model_dump_json(indent=4))
        except Exception as error:
            raise RuntimeError('Unknown error while saving catalog.') from error

    @classmethod
    def load(cls, catalog_filename: str = None):
        """
        Load the catalog from a JSON file.

        Parameters
        ----------
        catalog_filename : str, optional
            The filename to load the catalog from, by default None.

        Returns
        -------
        Catalog
            The loaded catalog.

        Raises
        ------
        RuntimeError
            If there is an error loading the catalog.
        """
        catalog_filename = catalog_filename or cls.catalog_filename
        try:
            with open(catalog_filename, 'r') as fp:
                catalog_data = json.load(fp)
                print(catalog_data)
                return Catalog(**catalog_data)
        except FileNotFoundError as error:
            raise RuntimeError('Catalog file not found.') from error

    def backup(self):
        """
        Backup the catalog.

        Raises
        ------
        NotImplementedError
            If the backup method is not implemented.
        """
        raise NotImplementedError

    def merge(
        self, catalog: 'Catalog', overwrite: bool = False, protected: list = None
    ):
        """
        Merge the given catalog into this catalog.

        Parameters
        ----------
        catalog : Catalog
            The catalog to merge.
        overwrite : bool, optional
            Whether to overwrite existing entries, by default False.
        protected : list, optional
            A list of fields that should not be overwritten, by default the list of manually added fields.
        """
        for entry in catalog:
            if entry.entry_id in self.entries:
                changed = self.entries[entry.entry_id].merge(
                    entry, overwrite=overwrite, protected=protected
                )
                continue
            self.entries[entry.entry_id] = entry
            changed = True
        if changed:
            self.modification_date = datetime.now()
