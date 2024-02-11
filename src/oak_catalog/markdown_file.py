"""Markdown file class."""

import yaml

from .catalog_entry import CatalogEntry
from .utils import validate_author, validate_date


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

        if not content_tokens[0].startswith(f"# {self.frontmatter['title']}") or not (
            '[Read on Omnivore]' in content_tokens[0]
            or '#omnivore' in content_tokens[0]
        ):
            print(content_tokens[0])
            raise RuntimeError('Markdown file is not from Omnivore.')

        if len(content_tokens) > 3 and content_tokens[2] == '## Highlights':
            self.frontmatter['highlights'] = [
                i.split(' [link]')[0] for i in content_tokens[3:]
            ]
        else:
            self.frontmatter['highlights'] = []

        if link := self.frontmatter.get('link'):
            domain = link.split('://')[1]
            if ':' in domain:
                domain = domain.split(':')[0]
            elif '/' in domain:
                domain = domain.split('/')[0]
            self.frontmatter['domain'] = domain

        # remove_from_title = [
        #     " - The Atlantic",
        #     " | WIRED",
        #     " - The New York Times",
        #     " - Vox",
        #     " | The New Yorker",
        #     " - The Verge",
        #     " | Hacker News",
        #     " | The Guardian",
        # ]
        # for item in remove_from_title:
        #     self.frontmatter["title"] = (
        #         self.frontmatter["title"].replace(item, "").strip()
        #     )

    def as_catalog_markdown(self, folder: str = './test'):
        """
        Convert the Omnivore Markdown file to a catalog Markdown file.

        Parameters
        ----------
        folder : str, optional
            The folder to save the catalog Markdown file, by default None.

        Returns
        -------
        CatalogEntryMarkdownFile
            The catalog Markdown file.
        """
        if not folder:
            folder = ''
        filename = f'article_{self.frontmatter["id"].lower()}.md'
        full_path = f'{folder}/{filename}'

        frontmatter = {
            'entry_id': self.frontmatter['id'],
            'entry_type': 'article',
            'title': self.frontmatter['title'],
            'author': validate_author(self.frontmatter.get('author')),
            'site_url': self.frontmatter.get('link'),
            'tags': self.frontmatter.get('tags', []),
            'protected_fields': ['entry_id'],
            'read_date': validate_date(self.frontmatter.get('date_saved')),
            'published_date': validate_date(self.frontmatter.get('date_published')),
            'markdown_filename': filename,
            'publisher': self.frontmatter.get('domain'),
        }
        content = '\n\n'.join(self.frontmatter['highlights'])

        return CatalogEntryMarkdownFile.from_data(frontmatter, content, full_path)


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
        self.frontmatter = self.catalog_entry.dict()
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

    @classmethod
    def from_data(cls, frontmatter, content, filename):
        """
        Create a catalog entry markdown file from data.

        Parameters
        ----------
        frontmatter : dict
            The frontmatter of the catalog entry.
        content : str
            The content of the catalog entry.
        filename : str
            The filename of the catalog entry.

        Returns
        -------
        CatalogEntryMarkdownFile
            The catalog entry markdown file.
        """
        catalog_entry = CatalogEntry(**frontmatter, description=content)
        result = cls(filename, skip_read=True)
        result.catalog_entry = catalog_entry
        return result

    def to_str(self):
        """
        Get the string representation of the catalog entry markdown file.

        Returns
        -------
        str
            The string representation of the catalog entry markdown file.
        """
        return '\n'.join(
            [
                f"{self.frontmatter['title']} ({self.frontmatter['publisher']})",
                f"by {self.frontmatter['author']}",
            ]
        )
