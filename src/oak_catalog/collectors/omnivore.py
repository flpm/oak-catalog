"""Class to collect data from the Omnivore folder."""

import favicon
import requests
from wand.exceptions import CorruptImageError
from wand.image import Image

from ..entry_data import EntryData, LinkEntryData
from ..folder import Folder
from ..utils import validate_author, validate_date
from .collector import Collector


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

    def collect_one_favicon(self, domain: str):
        """
        Collect the favicon to create a cover for the link.

        Parameters
        ----------
        domain : str
            The domain where to look for the favicon.

        Returns
        -------
        str
            The format of the image.
        bytes
            The image.
        """
        try:
            icons = favicon.get(f'http://{domain}')
        except Exception:
            icons = []
        image_bytes = None
        image_format = None
        for i in icons:
            if i.width >= 128:
                image_format = i.format
                try:
                    image_bytes = requests.get(i.url).content
                except Exception:
                    image_bytes = image_format = None
                else:
                    break
        else:
            for i in icons:
                if i.format in ('png', 'jpg', 'jpeg'):
                    image_format = i.format
                    try:
                        image_bytes = requests.get(i.url).content
                    except Exception:
                        image_bytes = image_format = None
                        continue
                    try:
                        img = Image(blob=image_bytes, format=image_format)
                    except CorruptImageError:
                        image_format = image_bytes = None
                        continue
                    if img.width > 128:
                        break
                else:
                    image_format = image_bytes = None
        if image_bytes and image_format:
            try:
                img = Image(blob=image_bytes, format=image_format)
            except CorruptImageError:
                return None, None
            if img.width > 256:
                img.transform(resize='256x')
            if img.height > 128:
                return image_format, img.make_blob(image_format)
        return None, None

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
        favicons = {}
        for frontmatter, content in self.folder.for_each_markdown():
            frontmatter['description'] = content
            entry = self.collect_one(frontmatter)
            if entry.domain in favicons:
                img_format, img_bytes = favicons[entry.domain]
            else:
                img_format, img_bytes = self.collect_one_favicon(entry.domain)
                favicons[entry.domain] = (img_format, img_bytes)
            if img_format and img_bytes:
                entry.cover_filename = f'{entry.domain.lower()}.{img_format}'
            yield (img_bytes, entry)
