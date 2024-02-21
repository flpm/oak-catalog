"""Class to represent the Oak catalog."""

from collections import Counter
from pathlib import Path

from .collector import OmnivoreCollector
from .entry import Entry
from .entry_data import LinkEntryData
from .folder import Folder


class OakCatalog:
    """
    Class to represent the Oak catalog.

    Attributes
    ----------
    catalog_folder : str
        The folder containing the catalog.
    source_collection : List[CatalogEntry]
        The source collection of the catalog.
    markdown_folder : str
        The folder containing the Markdown files.
    image_folder : str
        The folder containing the images.
    """

    source_collection = [
        {
            'name': 'Omnivore',
            'folder': Folder('../obsidian/Omnivore/'),
            'collector': OmnivoreCollector,
            'entry_class': LinkEntryData,
        }
    ]

    def __init__(self, catalog_folder: str = None):
        """
        Initialize the catalog.

        Parameters
        ----------
        catalog_folder : str
            The folder containing the catalog.
        """
        if catalog_folder is None:
            catalog_folder = Path().parent / 'output' / 'catalog'
        elif isinstance(catalog_folder, str):
            catalog_folder = Path(catalog_folder)
        elif isinstance(catalog_folder, Path):
            catalog_folder = catalog_folder
        else:
            raise ValueError('Invalid catalog_folder type')

        self.catalog_folder_path = catalog_folder
        self.catalog_folder_path.mkdir(parents=True, exist_ok=True)
        self.catalog_folder = Folder(self.catalog_folder_path)

        self.markdown_folder_path = self.catalog_folder_path / 'markdown'
        self.markdown_folder_path.mkdir(parents=True, exist_ok=True)
        self.markdown_folder = Folder(self.markdown_folder_path)

        self.image_folder_path = self.catalog_folder_path / 'images'
        self.image_folder_path.mkdir(parents=True, exist_ok=True)
        self.image_folder = Folder(self.image_folder_path)

    def build(self, sources: list = None):
        """
        Build the catalog.

        Parameters
        ----------
        sources : list, optional
            The sources to build the catalog from.
        """
        c = Counter()
        for source in self.source_collection:
            collector = source['collector'](
                source['folder'],
                entry_class=source['entry_class'],
            )
            for entry_data in collector.collect():
                entry = Entry.from_data(entry_data)
                entry.save(self.markdown_folder)

                if entry.data.theme:
                    c[entry.data.theme] += 1
        print(c.most_common(10))

    def backup(self, backup_folder: str = None):
        """
        Backup the catalog.

        Parameters
        ----------
        backup_folder : str, optional
            The folder to backup the catalog to.
        """
        raise NotImplementedError
