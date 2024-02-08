"""Markdown file class."""

import yaml

from .catalog_entry import CatalogEntry


class MarkdownFile:
    """
    A Markdown file.

    Attributes
    ----------
    filename : str
        The filename of the Markdown file.
    content : str
        The content of the Markdown file.
    frontmatter : dict
        The frontmatter of the Markdown file.
    """

    def __init__(self, filename: str, skip_read: bool = False):
        """
        Initialize a Markdown file.

        Parameters
        ----------
        filename : str
            The filename of the Markdown file.
        skip_read : bool, optional
            Whether to skip reading the Markdown file, by default False.
        """
        self.filename = filename
        self.content = ''
        self.frontmatter = {}

        if not skip_read:
            try:
                self.read()
            except FileNotFoundError:
                pass

    def __repr__(self):
        """
        Get the string representation of the Markdown file.

        Returns
        -------
        str
            The string representation of the Markdown file.
        """
        return f'MarkdownFile(filename={self.filename} frontmatter={len(self.frontmatter)} content={bool(self.content)})'

    def read(self):
        """
        Read a markdown file.
        """
        with open(self.filename, 'r') as fp:
            raw_content = fp.read()

        if raw_content.startswith('---\n'):
            frontmatter_raw, *content_raw = raw_content.split('---\n')[1:]
            self.content = '---\n'.join(content_raw).strip()
            self.frontmatter = {
                k: v.strip() if isinstance(v, str) else v
                for k, v in yaml.safe_load(frontmatter_raw).items()
            }
        else:
            self.content = raw_content.strip()
            self.frontmatter = {}

    def write(self, top_attributes: list = None):
        """
        Write a markdown file.

        Parameters
        ----------
        top_attributes : list, optional
            The attributes to put at the top of the frontmatter, by default None.
        """
        if not top_attributes:
            top_attributes = []

        top_frontmatter = {}
        bottom_frontmatter = {}

        for key, value in self.frontmatter.items():
            if key in top_attributes:
                top_frontmatter[key] = value
            else:
                bottom_frontmatter[key] = value

        frontmatter = {**top_frontmatter, **bottom_frontmatter}
        yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)
        with open(self.filename, 'w') as fp:
            fp.write('---\n')
            fp.write(yaml_frontmatter)
            fp.write('---\n')
            fp.write(self.content)
            fp.write('\n')

    def to_dict(self):
        """
        Convert the Markdown file to a dict.

        Returns
        -------
        dict
            The a dict version of the markdown.
        """
        result = {}
        result['filename'] = self.filename
        result['frontmatter'] = self.frontmatter.copy()
        result['content'] = self.content
        return result


class OmnivoreMarkdownFile(MarkdownFile):
    """
    A Markdown file from Omnivore.

    Attributes
    ----------
    filename : str
        The filename of the Markdown file.
    content : str
        The content of the Markdown file.
    frontmatter : dict
        The frontmatter of the Markdown file.
    highlights : List[str]
        The highlights of the Markdown file.
    """

    def read(self):
        """
        Read a markdown file created by Omnivore.
        """
        super().read()
        content_tokens = self.content.split('\n\n')

        if (
            not content_tokens[0].startswith(f"# {self.frontmatter['title']}")
            or '[Read on Omnivore]' not in content_tokens[0]
        ):
            print(content_tokens[0])
            raise RuntimeError('Markdown file is not from Omnivore.')

        if len(content_tokens) > 3 and content_tokens[2] == '## Highlights':
            self.frontmatter['highlights'] = [
                i.split(' [link]')[0] for i in content_tokens[3:]
            ]
        else:
            self.frontmatter['highlights'] = []

    def as_catalog_markdown(self):
        """
        Convert the Omnivore Markdown file to a catalog Markdown file.

        Returns
        -------
        CatalogEntryMarkdownFile
            The catalog Markdown file.
        """
        filename = f'./output/omnivore/{self.frontmatter["id"].lower()}.md'
        catalog_markdown = CatalogEntryMarkdownFile(filename, skip_read=True)
        catalog_markdown.frontmatter = self.frontmatter.copy()
        catalog_markdown.content = '\n\n'.join(self.frontmatter['highlights']) + '----'


class CatalogEntryMarkdownFile(MarkdownFile):
    """
    A Markdown file for a catalog entry.

    Attributes
    ----------
    filename : str
        The filename of the Markdown file.
    content : str
        The content of the Markdown file.
    frontmatter : dict
        The frontmatter of the Markdown file.
    catalog_entry : CatalogEntry
        The catalog entry of the Markdown file.
    """

    def __init__(
        self, filename: str, skip_read: bool = False, allow_overwrite: bool = False
    ):
        """
        Initialize a Markdown file for a catalog entry.

        Parameters
        ----------
        filename : str
            The filename of the Markdown file.
        skip_read : bool, optional
            Whether to skip reading the Markdown file, by default False.
        allow_overwrite : bool, optional
            Whether to allow overwriting fields, by default False.
        """
        super().__init__(filename, skip_read=True)
        self.catalog_entry = None
        self.allow_overwrite = allow_overwrite
        if not skip_read:
            self.read()

    def read(self):
        """
        Read a markdown file for a catalog entry.
        """
        super().read()
        read_catalog_entry = CatalogEntry(**self.frontmatter, description=self.content)
        if not self.catalog_entry:
            self.catalog_entry = read_catalog_entry
        else:
            if read_catalog_entry.protected_fields:
                protected = read_catalog_entry.protected_fields
            else:
                protected = None
            print(protected)
            self.catalog_entry.merge(
                read_catalog_entry, protected=protected, overwrite=self.allow_overwrite
            )

    def write(self, top_attributes: list = None):
        """
        Write a markdown file for a catalog entry.

        Parameters
        ----------
        top_attributes : list, optional
            The attributes to put at the top of the frontmatter, by default None.
        """
        self.frontmatter = self.catalog_entry.to_dict()
        del self.frontmatter['description']
        self.content = self.catalog_entry.description
        super().write(top_attributes=top_attributes)

    def protect_fields(self, fields: list):
        """
        Protect fields in the catalog entry.

        Parameters
        ----------
        fields : list
            The fields to protect.
        """
        self.catalog_entry.protected_fields = fields
