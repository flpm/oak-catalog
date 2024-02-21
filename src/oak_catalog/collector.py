"""Classes that collect data to create catalog entries."""

from .entry_data import EntryData, LinkEntryData
from .folder import Folder
from .utils import validate_author, validate_date


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


class OmnivoreCollector(Collector):
    """
    Collects data from Omnivore markdown files to create catalog entry.

    Attributes
    ----------
    folder : str | Folder
        The folder to collect data from.
    entry_class : EntryData, optional
            The entry class to use, by default LinkEntryData
    """

    def __init__(self, folder: str | Folder, entry_class: EntryData = LinkEntryData):
        """
        Initialize the collector.

        Parameters
        ----------
        folder : str | Folder
            The folder to collect data from.
        entry_class : EntryData, optional
            The entry class to use, by default EntryData

        Raises
        ------
        ValueError
            If the folder is not a string or a Folder instance.
        """
        self.entry_class = entry_class
        if isinstance(folder, Folder):
            self.folder = folder
        elif isinstance(folder, str):
            self.folder = Folder(folder)
        else:
            raise ValueError('Folder must be a string or a Folder instance')

    def collect_one(self, frontmatter: dict):
        """
        Collect data to create a catalog entry.

        Parameters
        ----------
        frontmatter : dict
            The data to create the catalog entry.

        Returns
        -------
        EntryData
            The catalog entry.
        """

        tags = set()
        theme = None
        entry_format = 'article'

        content = frontmatter['description']
        content_tokens = content.split('\n\n')

        if not content_tokens[0].startswith(f"# {frontmatter['title']}") or not (
            '[Read on Omnivore]' in content_tokens[0]
            or '#omnivore' in content_tokens[0]
        ):
            print(content_tokens[0])
            raise RuntimeError('Markdown file is not from Omnivore.')

        if len(content_tokens) > 3 and content_tokens[2] == '## Highlights':
            highlights = []
            summary = None
            for i in content_tokens[3:]:
                h_parts = i.split(' [link]')
                highlights.append(h_parts[0])
                if '$summary' in h_parts[1]:
                    summary = h_parts[0]
            if not summary and highlights:
                summary = highlights[0]

            frontmatter['highlights'] = highlights
            frontmatter['summary'] = summary
        else:
            frontmatter['highlights'] = []

        if link := frontmatter.get('link'):
            domain = link.split('://')[1]
            if ':' in domain:
                domain = domain.split(':')[0]
            elif '/' in domain:
                domain = domain.split('/')[0]
            frontmatter['domain'] = domain

        for entry in frontmatter.get('tags', []):
            if entry in ('article', 'website', 'video'):
                entry_format = entry
            if entry.startswith('_'):
                theme = entry.replace('_', '')
                tags.add(theme)
            else:
                tags.add(entry)

        filename = f"link_{frontmatter['id'].lower()}.md"
        new_frontmatter = {
            'entry_id': frontmatter['id'],
            'entry_type': 'link',
            'source': 'Omnivore',
            'title': frontmatter['title'],
            'full_title': frontmatter['title'],
            'author': validate_author(frontmatter.get('author')),
            'url': frontmatter.get('link'),
            'domain': frontmatter['domain'],
            'tags': list(tags),
            'format': entry_format,
            'theme': theme,
            'read_date': validate_date(frontmatter.get('date_saved')),
            'published_date': validate_date(frontmatter.get('date_published')),
            'markdown_filename': filename,
            'publisher': frontmatter.get('domain'),
            'summary': frontmatter.get('summary'),
            'description': '\n\n'.join(frontmatter['highlights']),
            'filename': f'link_{frontmatter["id"].lower()}.md',
        }
        return self.entry_class(**new_frontmatter)

    def collect(self):
        """
        Collect data to create catalog entries.

        Returns
        -------
        Iterator[EntryData], optional
            The catalog entry, by default EntryData.
        """
        for frontmatter, content in self.folder.for_each_markdown():
            frontmatter['description'] = content
            yield self.collect_one(frontmatter)
