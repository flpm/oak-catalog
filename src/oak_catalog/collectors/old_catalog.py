"""Class to collect data from the old catalog."""

import json
from collections import Counter
from pathlib import Path

from wand.image import Image

from ..entry_data import AudiobookEntryData, BookEntryData, EntryData
from .collector import Collector


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
        image_folder: str | Path | None = None,
        book_entry_class: EntryData = BookEntryData,
        audiobook_entry_class: EntryData = AudiobookEntryData,
    ):
        """
        Initialize the collector.

        Parameters
        ----------
        catalog_file : str | Path
            The file to collect data from.
        image_folder : str | Path
            The folder containing the images.
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
        if image_folder is None:
            self.image_folder = None
        elif isinstance(image_folder, Path):
            self.image_folder = image_folder
        else:
            self.image_folder = Path(image_folder)

    def collect(self):
        """
        Collect data to create catalog entries.

        Yields
        ------
        bytes
            The cover image bytes.
        Iterator[EntryData]
            The catalog entries.
        """
        c = Counter()
        t = Counter()
        bytes_size = 0
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

                    image_bytes = None
                    if self.image_folder and (cover := book.get('cover_filename')):
                        image_path = self.image_folder / cover
                        with Image(filename=image_path) as img:
                            # ! This particular book cover causes a segfault in ImageMagick, so we skip it
                            # B08ZYXLTYG Beginner's Mind by Yo-Yo Ma
                            if book_id not in ('B08ZYXLTYG'):
                                if img.width > 256:
                                    img.transform(resize='256x')
                                image_bytes = img.make_blob(format='jpeg')
                                bytes_size += len(image_bytes)
                    if book_type == 'book':
                        yield (image_bytes, self.book_entry_class(**book))
                    elif book_type == 'audiobook':
                        yield (image_bytes, self.audiobook_entry_class(**book))

            print(bytes_size)
