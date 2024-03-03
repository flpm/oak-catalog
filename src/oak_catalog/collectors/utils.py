"""Utility functions for the collectors module."""

import requests
from wand.exceptions import CorruptImageError
from wand.image import Image


def get_image(domain, format, url, image_cache_folder):
    """
    Get the image from the url or the local cache.

    Parameters
    ----------
    domain : str
        The domain of the image.
    format : str
        The format of the image.
    url : str
        The url of the image.
    image_cache_folder : Folder
        The folder containing the cached images.
    """
    cache_name = f'{domain.lower()}.{format}'
    cached_image = image_cache_folder.read_image(cache_name)
    if cached_image:
        return Image(blob=cached_image, format=format)

    try:
        response = requests.get(url)
    except Exception:
        return None
    if response.status_code == 200:
        try:
            try:
                image = Image(blob=response.content, format=format)
            except CorruptImageError:
                return None
            image_cache_folder.write_image(cache_name, response.content)
            return image
        except CorruptImageError:
            return None
    return None
