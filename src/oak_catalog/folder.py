"""Represents a folder in the filesystem."""

from pathlib import Path

import yaml

from .entry_data import EntryData


class Folder:
    """
    Represents a folder in the filesystem.

    Attributes
    ----------
    path_raw : str
        The raw path of the folder.
    path : Path
        The Path object of the folder.

    Parameters
        ----------
        folder_path : str
            The path of the folder.
        create : bool, optional
            Whether to create the folder if it does not exist, by default False.
    """

    def __init__(self, folder_path: Path | str, create: bool = True):
        """
        Initialize a folder.

        Parameters
        ----------
        folder_path : Path | str
            The path of the folder.
        create : bool, optional
            Whether to create the folder if it does not exist, by default False.
        """
        if isinstance(folder_path, str):
            self.path = Path(folder_path)
        else:
            self.path = folder_path

        if create:
            self.create()

    def __repr__(self):
        """
        Get the string representation of the folder.

        Returns
        -------
        str
            The string representation of the folder.
        """

        result = f'Folder(path={self.path}'
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

    def for_each(self, glob: str = '*', recursive: bool = False):
        """
        Iterate over each file in the folder.

        Parameters
        ----------
        glob : str, optional
            The glob pattern to use to find files, by default "*".
        recursive : bool, optional
            Whether to search recursively, by default False.

        Yields
        ------
        Path
            The file.
        """
        if recursive:
            glob = f'**/{glob}'
        for file in self.path.glob(glob):
            yield file

    def for_each_markdown(self, recursive: bool = True):
        """
        Iterate over each markdown file in the folder.

        Parameters
        ----------
        recursive : bool, optional
            Whether to search recursively, by default False.

        Yields
        ------
        dict
            The frontmatter of the markdown file.
        str
            The content of the markdown file.
        """
        for markdown_file in self.for_each(glob='*.md', recursive=recursive):
            yield self.read_markdown(markdown_file)

    def read_image(self, filename: str | Path):
        """
        Read an image file.

        Parameters
        ----------
        filename : str | Path
            The filename of the image file.

        Returns
        -------
        bytes
            The content of the image file.
        """
        if isinstance(filename, Path):
            file = filename
        else:
            file = self.path / filename

        try:
            with file.open('rb') as fp:
                return fp.read()
        except FileNotFoundError:
            return None

    def write_image(self, filename: str | Path, content: bytes):
        """
        Write an image file.

        Parameters
        ----------
        filename : str | Path
            The filename of the image file.
        content : bytes
            The content of the image file.
        """
        if isinstance(filename, Path):
            file = filename
        else:
            file = self.path / filename

        with file.open('wb') as fp:
            fp.write(content)

    def write_markdown(
        self,
        filename: str | Path,
        frontmatter: dict,
        content: str,
        top_attributes: list = None,
    ):
        """
        Write a markdown file.

        Parameters
        ----------
        filename : str | Path
            The filename of the markdown file.
        frontmatter : dict
            The frontmatter of the markdown file.
        content : str
            The content of the markdown file.
        top_attributes : list, optional
            The attributes to put at the top of the frontmatter, by default None.
        """
        if not top_attributes:
            top_attributes = []

        top_frontmatter = {}
        bottom_frontmatter = {}

        for key, value in frontmatter.items():
            if key in top_attributes:
                top_frontmatter[key] = value
            else:
                bottom_frontmatter[key] = value

        frontmatter = {**top_frontmatter, **bottom_frontmatter}
        yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)

        if isinstance(filename, Path):
            file = filename
        else:
            file = self.path / filename

        with file.open('w') as fp:
            fp.write('---\n')
            fp.write(yaml_frontmatter)
            fp.write('---\n')
            if content:
                fp.write(content)
            # fp.write('\n')

    def read_markdown(self, filename: str | Path):
        """
        Read a markdown file.

        Parameters
        ----------
        filename : str | Path
            The filename of the markdown file.

        Returns
        -------
        dict
            The frontmatter of the markdown file.
        str
            The content of the markdown file.
        """

        if isinstance(filename, Path):
            file = filename
        else:
            file = self.path / filename

        with file.open('r') as fp:
            raw_content = fp.read()

        if raw_content.startswith('---\n'):
            frontmatter_raw, *content_raw = raw_content.split('---\n')[1:]
            content = '---\n'.join(content_raw).strip()
            frontmatter = {
                k: v.strip() if isinstance(v, str) else v
                for k, v in yaml.safe_load(frontmatter_raw).items()
            }
        else:
            content = raw_content.strip()
            frontmatter = {}

        return frontmatter, content

    def write_entry(
        self, filename: str | Path, entry: EntryData, top_attributes: list = None
    ):
        """
        Write an entry to a file.

        Parameters
        ----------
        filename : str | Path
            The filename of the entry file.
        entry : EntryData
            The entry to write.
        top_attributes : list, optional
            The attributes to put at the top of the frontmatter, by default None.
        """
        if isinstance(filename, Path):
            file = filename
        else:
            file = self.path / filename

        frontmatter = entry.model_dump()
        del frontmatter['description']
        content = getattr(entry, 'description', '')

        self.write_markdown(file, frontmatter, content, top_attributes=top_attributes)

    def save_entry(
        self, filename: str, entry: EntryData, prevent_overwrite: bool = False
    ):
        """
        Save an entry to a file.

        Parameters
        ----------
        filename : str
            The filename of the entry file.
        entry : EntryData
            The entry to save.
        prevent_overwrite : bool, optional
            Whether to prevent overwriting existing entries, by default False.
        """
        current_file_entry = self.read_entry(filename, entry.__class__)
        if current_file_entry:
            current_file_entry.merge(
                entry,
                prevent_overwrite=prevent_overwrite,
                protected=current_file_entry.protected_fields,
            )
        else:
            current_file_entry = entry
        self.write_entry(filename, current_file_entry)

    def read_entry(self, filename: str, entry_class: EntryData = EntryData):
        """
        Read an entry from a file.

        Parameters
        ----------
        filename : str
            The filename of the entry file.
        entry_class : EntryData, optional
            The class of the entry, by default EntryData.

        Returns
        -------
        EntryData
            The entry read from the file.
        """
        try:
            frontmatter, content = self.read_markdown(filename)
        except FileNotFoundError:
            return None
        entry = entry_class(**frontmatter)
        entry.description = content
        return entry
