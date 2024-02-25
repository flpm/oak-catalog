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
        'ancient-history': 'history',
        'writing': 'writing',
        'design': 'design',
        'game-of-go': 'go',
        'role-playing-games': 'rpg',
        'learning-latin': 'latin',
        'reading': 'reading',
        'language': 'language',
        'linguistics': 'language',
        'epigraphy': 'history',
        'mythology': 'history',
        'security': 'software',
        'software': 'software',
        'typography': 'design',
        'internet': 'web',
        'math': 'data',
        'visualization': 'data',
        'data': 'data',
        'graphs': 'data',
        'archaeology': 'history',
        'psychology': 'humans',
        'sociology': 'humans',
        'anthropology': 'humans',
        'autism': 'humans',
        'anxiety': 'humans',
        'computational-design': 'design',
        'economics': 'humans',
        'engineering': None,
        'philosophy': 'humans',
        'novel': None,
        'graphic-novels': None,
        'fantasy': None,
        'biography': 'memoir',
        'business': None,
        'essays': None,
        'crime-None': None,
        'science': None,
        'history': 'history',
        'humor': 'memoirs',
        'paris': None,
        'urbanism': None,
        'making': 'making',
        'drama': None,
        'poetry': None,
        'entrepreneurship': None,
        'short-stories': None,
        'historical-novel': None,
        'medieval-history': 'history',
        'logic': None,
        'financial-markets': None,
        'photography': None,
        'puzzles': None,
        'magic': 'thinking',
        'music': 'memoirs',
        'presentation': 'writing',
        'pop-up': None,
        'ciphers': 'software',
        'labyrinths': 'labyrinths',
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
        t = Counter()
        with open(self.catalog_file, 'r') as f:
            catalog_json = json.load(f)
            for book_id, book_types in catalog_json.items():
                for book_type, book in book_types.items():
                    if book_type == 'audiobook_sample':
                        continue
                    book['entry_id'] = book_id
                    book['entry_type'] = book_type
                    if book.get('protected_fields'):
                        del book['protected_fields']
                    if book.get('authors'):
                        book['author'] = book['authors']
                    else:
                        continue
                    if book_type == 'audiobook':
                        if book.get('narrators'):
                            book['narrator'] = book.get('narrators')
                        else:
                            continue
                        if length := book.get('length'):
                            hours = int(length) // 1000 // 3600
                            minutes = round(int(length) / 1000 / 60 % 60)
                            book['length'] = f'{hours}h {minutes}m'

                    if 'tags' not in book:
                        book['tags'] = set()
                    if topics := book.get('topics'):
                        for one_topic in topics:
                            raw_topic = one_topic.replace('&', ',')
                            raw_topic = raw_topic.replace('/', ',')
                            raw_topic = raw_topic.replace('--', ',')
                            raw_topic = raw_topic.replace(' and ', ',')
                            topic_list = set()
                            for i in raw_topic.split(','):
                                if ':' in i:
                                    i = i.split(':')[0]
                                if ' - ' in i:
                                    i = i.split(' - ')[0]
                                i = i.strip().lower()
                                if 'go (game)' in i:
                                    i = 'go game'
                                if 'etc' in i:
                                    continue
                                if i == 'ya)':
                                    continue
                                if '(' in i:
                                    if 'typography' in i:
                                        i = 'typography'
                                    i = i.split('(')[0].strip()
                                if i.startswith('f2521') or i.startswith('gv1469.'):
                                    continue
                                if i.startswith('u.s.'):
                                    i = i.replace('u.s.', 'us')
                                if i == 'go':
                                    i = 'go game'
                                if i:
                                    i = i.replace(' ', '-')
                                    topic_list.add(i)
                            t.update(topic_list)
                            book['tags'].update(topic_list)

                    book['length'] = str(book.get('length'))

                    book['source'] = book['source'].lower()
                    if theme := book.get('theme'):
                        theme = theme.strip().replace(' ', '-')
                        if new_theme := self.theme_map.get(theme):
                            book['theme'] = new_theme
                        else:
                            book['theme'] = None
                            book['tags'].add(theme)

                    c[len(book['tags'])] += 1

                    if book_type == 'book':
                        yield self.book_entry_class(**book)
                    elif book_type == 'audiobook':
                        yield self.audiobook_entry_class(**book)
