"""Represents an Entry in the catalog."""

from .entry_data import EntryData
from .folder import Folder


class Entry:
    """Represents an Entry in the catalog."""

    def __init__(self, entry_type: str, entry_id: str, data: EntryData) -> None:
        """
        Initialize an Entry.

        Parameters
        ----------
        entry_type : str
            The type of the entry.
        entry_id : str
            The ID of the entry.
        data : EntryData
            The data of the entry.
        """
        self.entry_id = entry_id
        self.entry_type = entry_type
        self.filename = f'{entry_type}_{entry_id}.md'
        self.data = data

    @classmethod
    def from_dict(cls, data) -> 'Entry':
        """
        Create an Entry from data.

        Parameters
        ----------
        data : dict
            The data of the entry.

        Returns
        -------
        Entry
            The Entry.
        """
        return cls(data['entry_type'], data['entry_id'], data)

    @classmethod
    def from_data(cls, data: EntryData) -> None:
        """
        Create an Entry from data.

        Parameters
        ----------
        data : EntryData
            The data of the entry.
        """
        return Entry(data.entry_type, data.entry_id, data)

    def to_dict(self) -> dict:
        """
        Convert the Entry to a dictionary.

        Returns
        -------
        dict
            The dictionary representation of the Entry.
        """
        return self.data.model_dump()

    def __repr__(self) -> str:
        """
        Get the string representation of the Entry.

        Returns
        -------
        str
            The string representation of the Entry.
        """
        return f"{self.__class__.__name__}({self.entry_type}|{self.entry_id} {getattr(self.data, 'title', 'Missing Title')})"

    def save(self, folder: Folder) -> None:
        """
        Save the Entry to a folder.

        Parameters
        ----------
        folder : Folder
            The folder to save the Entry to.
        """
        folder.save_file(self.filename, self.data)

    def load(self, folder: Folder) -> None:
        """
        Load the Entry from a folder.

        Parameters
        ----------
        folder : Folder
            The folder to load the Entry from.
        """
        self.data = folder.load_file(self.filename)
