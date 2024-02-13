"""Class to represent the Oak catalog."""

from collections import Counter

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
            "name": "Omnivore",
            "folder": "../obsidian/Omnivore/",
            "collector": MarkdownCollector,
            "factory": OmnivoreMarkdownFile,
            "recursive": True,
        }
    ]

    markdown_folder = "markdown"
    image_folder = "images"

    def __init__(self, catalog_folder: str = "./output"):
        """
        Initialize the catalog.

        Parameters
        ----------
        catalog_folder : str
            The folder containing the catalog.
        """
        self.catalog_folder = catalog_folder

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
            collector = source["collector"]
            factory = source["factory"]
            folder = source["folder"]
            recursive = source.get("recursive", False)
            collector = collector(folder, recursive=recursive)
            for entry in collector.collect(factory=factory):
                catalog = entry.as_catalog_markdown(
                    folder=f"{self.catalog_folder}/{self.markdown_folder}"
                )
                catalog.write()

                if catalog.catalog_entry.theme:
                    # print(catalog.filename)
                    # print(catalog.to_str())
                    # print(catalog.catalog_entry.tags)
                    c[catalog.catalog_entry.theme] += 1
                    # print("---")
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
