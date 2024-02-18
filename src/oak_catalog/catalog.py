"""Class to represent the Oak catalog."""

from collections import Counter
from pathlib import Path

from .collector import MarkdownCollector
from .markdown_file import OmnivoreMarkdownFile


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
            'folder': Path('../obsidian/Omnivore/'),
            'collector': MarkdownCollector,
            'factory': OmnivoreMarkdownFile,
            'recursive': True,
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

        self.catalog_folder = catalog_folder

        self.markdown_folder = self.catalog_folder / 'markdown'
        self.markdown_folder.mkdir(parents=True, exist_ok=True)

        self.image_folder = self.catalog_folder / 'images'
        self.image_folder.mkdir(parents=True, exist_ok=True)

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
            collector = source['collector']
            factory = source['factory']
            folder = source['folder']
            recursive = source.get('recursive', False)
            collector = collector(folder, recursive=recursive)
            for entry in collector.collect(factory=factory):
                entry_md = entry.as_catalog_markdown(folder=self.markdown_folder)
                entry_md.write()

                if entry_md.catalog_entry.theme:
                    c[entry_md.catalog_entry.theme] += 1
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
