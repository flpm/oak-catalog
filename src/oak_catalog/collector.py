"""Classes that collect data to create catalog entries."""

import json
from collections import Counter
from pathlib import Path

from .entry_data import AudiobookEntryData, BookEntryData, EntryData, LinkEntryData
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


class OldCatalogCollector(Collector):
    """
    Collect data from old catalog markdown files to create catalog entry.

    Attributes
    ----------
    folder : str | Folder
        The folder to collect data from.
    book_entry_class : EntryData, optional
        The entry class to use for books, by default BookEntryData.
    audiobook_entry_class : EntryData
        The entry class to use for audiobooks, by default AudiobookEntryData.
    """

    theme_map = {
        'ancient-history': 'ancient-history',
        'writing': 'writing',
        'design': 'design',
        'game-of-go': 'game-of-go',
        'role-playing-games': 'role-playing-games',
        'learning-latin': 'learning-latin',
        'reading': 'reading',
        'language': 'language',
        'linguistics': 'language',
        'epigraphy': 'ancient-history',
        'mythology': 'ancient-history',
        'security': 'engineering',
        'software': 'engineering',
        'typography': 'design',
        'internet': 'web',
        'math': 'data',
        'visualization': 'data',
        'data': 'data',
        'graphs': 'data',
        'archaeology': 'ancient-history',
        'psychology': 'social-sciences',
        'sociology': 'social-sciences',
        'anthropology': 'social-sciences',
        'autism': 'social-sciences',
        'anxiety': 'social-sciences',
        'computational-design': 'design',
        'economics': 'social-sciences',
        'engineering': 'engineering',
        'philosophy': 'philosophy',
        'novel': 'fiction',
        'graphic-novels': 'fiction',
        'fantasy': 'fiction',
        'biography': 'memoir',
        'business': 'non-fiction',
        'essays': 'non-fiction',
        'crime-fiction': 'fiction',
        'science': 'non-fiction',
        'history': 'non-fiction',
        'humor': 'memoirs',
        'paris': 'fiction',
        'urbanism': 'social-sciences',
        'making': 'making',
        'drama': 'fiction',
        'poetry': 'fiction',
        'entrepreneurship': 'non-fiction',
        'short-stories': 'fiction',
        'historical-novel': 'fiction',
        'medieval-history': 'non-fiction',
        'logic': 'non-fiction',
        'financial-markets': 'social-sciences',
        'photography': 'non-fiction',
        'puzzles': 'non-fiction',
        'magic': 'magic',
        'music': 'non-fiction',
        'presentation': 'writing',
        'pop-up': 'non-fiction',
        'ciphers': 'engineering',
        'labyrinths': 'social-sciences',
    }

    def __init__(
        self,
        catalog_file: str | Path,
        book_entry_class: EntryData = BookEntryData,
        audiobook_entry_class: EntryData = AudiobookEntryData,
    ):
        """
        Initialize the collector.

        Parameters
        ----------
        catalog_file : str | Path
            The file to collect data from.
        book_entry_class : EntryData
            The entry class to use for books, by default BookEntryData.
        audiobook_entry_class : EntryData
            The entry class to use for audiobooks, by default AudiobookEntryData.

        Raises
        ------
        ValueError
            If the folder is not a string or a Folder instance.
        """
        self.book_entry_class = book_entry_class
        self.audiobook_entry_class = audiobook_entry_class
        if isinstance(catalog_file, Path):
            self.catalog_file = catalog_file
        else:
            self.catalog_file = Path(catalog_file)

    def collect(self):
        """
        Collect data to create catalog entries.

        Returns
        -------
        Iterator[EntryData]
            The catalog entries.
        """
        c = Counter()
        with open(self.catalog_file, 'r') as f:
            catalog_json = json.load(f)
            for book_id, book_types in catalog_json.items():
                for book_type, book in book_types.items():
                    if book_type == 'audiobook_sample':
                        continue
                    book['entry_id'] = book_id
                    book['entry_type'] = book_type
                    if book.get('authors'):
                        book['author'] = book['authors']
                    else:
                        continue
                    if book_type == 'audiobook':
                        if book.get('narrators'):
                            book['narrator'] = book.get('narrators')
                        else:
                            continue
                    book['length'] = str(book.get('length'))

                    book['source'] = book['source'].lower()
                    if theme := book.get('theme'):
                        theme = theme.replace(' ', '-')
                        if new_theme := self.theme_map.get(theme):
                            book['theme'] = new_theme
                        else:
                            book['theme'] = None
                            book['tags'] = [theme]
                            c[theme] += 1

                    if book_type == 'book':
                        yield self.book_entry_class(**book)
                    elif book_type == 'audiobook':
                        yield self.audiobook_entry_class(**book)
        print(book.keys())
        print(c.most_common())
