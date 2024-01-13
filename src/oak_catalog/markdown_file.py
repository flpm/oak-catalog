"""Markdown file class."""

import yaml


class MarkdownFile:
    """
    A Markdown file.

    Attributes
    ----------
    filename : str
        The filename of the Markdown file.
    raw_content : str
        The raw content of the Markdown file.
    content : str
        The content of the Markdown file.
    frontmatter : dict
        The frontmatter of the Markdown file.
    """

    def __init__(self, filename: str):
        """
        Initialize a Markdown file.

        Parameters
        ----------
        filename : str
            The filename of the Markdown file.
        """
        self.filename = filename
        self.raw_content = ''
        self.content = ''
        self.frontmatter = {}

        try:
            self.read()
        except FileNotFoundError:
            pass

    def read(self):
        """
        Read a markdown file.
        """
        with open(self.filename, 'r') as fp:
            self.raw_content = fp.read()

        if self.raw_content.startswith('---\n'):
            frontmatter_raw, *content_raw = self.raw_content.split('---\n')[1:]
            self.content = '---\n'.join(content_raw).strip()
            self.frontmatter = {
                k: v.strip() if isinstance(v, str) else v
                for k, v in yaml.safe_load(frontmatter_raw).items()
            }
        else:
            self.content = self.raw_content.strip()
            self.frontmatter = {}


class OmnivoreMarkdownFile(MarkdownFile):
    """
    A Markdown file from Omnivore.

    Attributes
    ----------
    filename : str
        The filename of the Markdown file.
    raw_content : str
        The raw content of the Markdown file.
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
            self.highlights = content_tokens[3:]
        else:
            self.highlights = []
