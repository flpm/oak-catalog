"""Utility functions for the collectors module."""

import requests
from wand.exceptions import CorruptImageError, OptionError
from wand.image import Image


def get_image_from_cache(image_cache_folder, cache_name):
    """
    Get an image from the cache.

    Parameters
    ----------
    image_cache_folder : Folder
        The folder containing the cached images.
    cache_name : str
        The name of the image in the cache.

    Returns
    -------
    Image
        The image.
    """
    cached_image = image_cache_folder.read_image(cache_name)
    if cached_image:
        try:
            return Image(blob=cached_image, format=cache_name.split('.')[1])
        except (CorruptImageError, OptionError):
            return None
    return None


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

    Returns
    -------
    Image
        The image as a wand.image.Image instance.
    """
    cache_name = f'{domain.lower()}.{format}'
    cached_image = get_image_from_cache(image_cache_folder, cache_name)
    if cached_image:
        return cached_image

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
