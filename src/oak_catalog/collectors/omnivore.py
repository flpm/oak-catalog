"""Class to collect data from the Omnivore folder."""

import favicon

from ..entry_data import EntryData, LinkEntryData
from ..folder import Folder
from ..utils import validate_author, validate_date
from .collector import Collector
from .utils import get_image, get_image_from_cache


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

    def __init__(
        self,
        folder: str | Folder,
        entry_class: EntryData = LinkEntryData,
        image_cache_folder: str | Folder = None,
    ):
        """
        Initialize the collector.

        Parameters
        ----------
        folder : str | Folder
            The folder to collect data from.
        entry_class : EntryData, optional
            The entry class to use, by default EntryData
        image_cache_folder : str | Folder
            The folder to cache the images, by default './work/images'.

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
        if image_cache_folder is None:
            image_cache_folder = './work/images'
        if isinstance(image_cache_folder, Folder):
            self.image_cache_folder = image_cache_folder
        elif isinstance(image_cache_folder, str):
            self.image_cache_folder = Folder(image_cache_folder)
        else:
            raise ValueError('Image cache folder must be a string or a Folder instance')
        self.image_cache_folder.create()

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
        image = image_format = None
        for image_format in ('png', 'jpg', 'jpeg'):
            image = get_image_from_cache(
                self.image_cache_folder, cache_name=f'{domain.lower()}.{image_format}'
            )
            if image:
                break
        else:
            image = None
            image_format = None
            try:
                icons = favicon.get(f'http://{domain}')
            except Exception:
                icons = []

            for i in icons:
                if i.width >= 128:
                    image_format = i.format
                    image = get_image(domain, i.format, i.url, self.image_cache_folder)
                    if image:
                        break
                else:
                    image_format = image = None
            else:
                for i in icons:
                    if i.format in ('png', 'jpg', 'jpeg'):
                        image_format = i.format
                        image = get_image(
                            domain, i.format, i.url, self.image_cache_folder
                        )
                        if not image:
                            continue
                        if image.width > 128:
                            break
                    else:
                        image_format = image = None

        if image_format and image:
            if image.width > 256:
                image.transform(resize='256x')
            if image.height > 128:
                return image_format, image.make_blob(image_format)

        # If no favicon is found, use a default one
        default_image = get_image_from_cache(
            self.image_cache_folder, cache_name='missing.png'
        )
        default_image.transform(resize='256x')
        return 'png', default_image.make_blob('png')

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
