"""Classes that collect data to create catalog entries."""

from .folder import Folder
from .markdown_file import MarkdownFile


class Collector:
    """
    Base class for collectors.
    """

    def __init__(self):
        pass

    def collect(self):
        """
        Collect data to create catalog entries.

        Returns
        -------
        Iterator[CatalogEntry]
            The catalog entries.
        """
        raise NotImplementedError


class FolderCollector(Collector):
    """
    Collects data from a files in a folder to create a catalog entries.

    Attributes
    ----------
    folder : str
        The folder to collect data from.
    glob : str, optional
        The glob pattern to match files in the folder, by default "*.md"
    recursive : bool, optional
        Whether to search recursively, by default False
    """

    def __init__(self, folder: str, glob='*', recursive=False):
        self.folder = folder
        self.glob = glob
        self.recursive = recursive

    def _collect_from_file(self, file: str, factory=lambda x: x):
        """
        Collect data from a file to create a catalog entry.

        Parameters
        ----------
        file : str
            The file to collect data from.
        factory : callable, optional
            The factory to use to create catalog entries, by default lambda x: x.

        Returns
        -------
        CatalogEntry
            The catalog entry.
        """
        return factory(file)

    def collect(self, factory=lambda x: x):
        """
        Collect data to create catalog entries.

        Parameters
        ----------
        factory : callable, optional
            The factory to use to create catalog entries, by default lambda x: x.

        Returns
        -------
        Iterator[CatalogEntry]
            The catalog entries.
        """

        if self.folder is None:
            raise ValueError('Folder not specified')

        folder = Folder(self.folder)
        for file in folder.for_each(
            lambda x: x, glob=self.glob, recursive=self.recursive
        ):
            yield self._collect_from_file(file, factory=factory)


class MarkdownCollector(FolderCollector):
    """
    Collects data from Markdown files in a folder to create a catalog entries.

    Attributes
    ----------
    folder : str
        The folder to collect data from.
    glob : str, optional
        The glob pattern to match files in the folder, by default "*.md"
    recursive : bool, optional
        Whether to search recursively, by default False
    """

    def __init__(
        self,
        folder: str,
        glob='*.md',
        recursive=False,
    ):
        super().__init__(folder, glob, recursive)

    def collect(self, factory=MarkdownFile):
        """
        Collect data to create catalog entries.

        Parameters
        ----------
        factory : callable, optional
            The factory to use to create catalog entries, by default lambda x: x.

        Returns
        -------
        Iterator[CatalogEntry]
            The catalog entries.
        """
        return super().collect(factory=factory)

    def _collect_from_file(self, file: str, factory):
        """
        Collect data from a Markdown file to create a catalog entry.

        Parameters
        ----------
        file : str
            The file to collect data from.
        factory : callable
            The factory to use to read the file entries.

        Returns
        -------
        CatalogEntry
            The catalog entry.
        """
        return factory(file)
