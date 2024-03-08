"""Class to represent the Oak catalog."""

from collections import Counter
from pathlib import Path

from .collectors.old_catalog import OldCatalogCollector
from .collectors.omnivore import OmnivoreCollector
from .entry import Entry
from .entry_data import AudiobookEntryData, BookEntryData, LinkEntryData
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
            'params': {
                'folder': Folder('../obsidian/Omnivore/'),
                'entry_class': LinkEntryData,
            },
            'collector': OmnivoreCollector,
        },
        {
            'name': 'Old Catalog',
            'params': {
                'catalog_file': Path('../oak/work/catalogue.json'),
                'image_folder': Path('../oak/output/covers'),
                'book_entry_class': BookEntryData,
                'audiobook_entry_class': AudiobookEntryData,
            },
            'collector': OldCatalogCollector,
        },
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

    def build(self, override_images: bool = False, sources: list = None):
        """
        Build the catalog.

        Parameters
        ----------
        override_images : bool, optional
            Whether to override the images, by default False.
        sources : list, optional
            The sources to build the catalog from.
        """
        c = Counter()
        for source in self.source_collection:
            print(f"Collecting from {source['name']}: ", end='')
            for label, attribute in source.get('dynamic_params', {}).items():
                source['params'][label] = getattr(self, attribute)
            collector = source['collector'](**source['params'])
            for cover_bytes, entry_data in collector.collect():
                c[source['name']] += 1
                if cover_bytes and entry_data.cover_filename:
                    filepath = self.image_folder_path / entry_data.cover_filename
                    if override_images or not filepath.exists():
                        with open(filepath, 'wb') as cover_file:
                            cover_file.write(cover_bytes)
                            print('+', end='')
                    else:
                        print('=', end='')
                else:
                    print('.', end='')
                entry = Entry.from_data(entry_data)
                entry.save(self.markdown_folder)
            print(f" finished ({c[source['name']]} entries)")

    def backup(self, backup_folder: str = None):
        """
        Backup the catalog.

        Parameters
        ----------
        backup_folder : str, optional
            The folder to backup the catalog to.
        """
        raise NotImplementedError
