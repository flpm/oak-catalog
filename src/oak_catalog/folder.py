"""Represents a folder in the filesystem."""

from pathlib import Path


class Folder:
    """
    Represents a folder in the filesystem.

    Attributes
    ----------
    path_raw : str
        The raw path of the folder.
    path : Path
        The Path object of the folder.
    """

    def __init__(self, folder_path: str):
        """
        Initialize a folder.

        Parameters
        ----------
        folder_path : str
            The path of the folder.
        """
        self.path_raw = folder_path
        self.path = Path(folder_path)

    def __repr__(self):
        """
        Get the string representation of the folder.

        Returns
        -------
        str
            The string representation of the folder.
        """

        result = f'Folder(path={self.path_raw}'
        if self.exists():
            result += ' exists)'
        else:
            result += ' non-existent)'
        return result

    def exists(self):
        """
        Check if the folder exists.

        Returns
        -------
        bool
            True if the folder exists, False otherwise.
        """
        return self.path.exists() and self.path.is_dir()

    def create(self):
        """
        Create the folder.
        """
        self.path.mkdir(parents=True, exist_ok=True)

    def delete(self):
        """
        Delete the folder.
        """
        self.path.rmdir()

    def for_each(self, func: callable, glob: str = '*', recursive: bool = False):
        """
        Call the given function for each file in the folder.

        Parameters
        ----------
        func : callableFolder()
            The function to call for each file.
        glob : str, optional
            The glob pattern to use to find files, by default "*".
        recursive : bool, optional
            Whether to search recursively, by default False.
        """
        if recursive:
            glob = f'**/{glob}'
        for file in self.path.glob(glob):
            yield func(file)
